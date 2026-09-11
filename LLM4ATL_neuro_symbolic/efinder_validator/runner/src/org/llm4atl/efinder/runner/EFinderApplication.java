package org.llm4atl.efinder.runner;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.equinox.app.IApplication;
import org.eclipse.equinox.app.IApplicationContext;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EcorePackage;
import org.eclipse.emf.ecore.EReference;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.util.EcoreUtil;
import org.eclipse.emf.ecore.xmi.XMIResource;
import org.eclipse.emf.ecore.xmi.impl.EcoreResourceFactoryImpl;
import org.eclipse.emf.ecore.xmi.impl.XMIResourceFactoryImpl;
import org.eclipse.ocl.pivot.ExpressionInOCL;
import org.eclipse.ocl.pivot.Model;
import org.eclipse.ocl.pivot.resource.ASResource;
import org.eclipse.ocl.pivot.utilities.OCL;
import org.eclipse.ocl.xtext.completeocl.CompleteOCLStandaloneSetup;

import efinder.core.IBoundsProvider;
import efinder.core.IModelFinder.Result;
import efinder.core.IModelFinder.Status;
import efinder.emfocl.runner.EFinderRunner;
import efinder.usemv.UseMvFinder;
import efinder.usemv.UseMvResult;

/** Headless Eclipse entry point for a single ATL2TM Ecore counterexample check. */
public final class EFinderApplication implements IApplication {
    @Override
    public Object start(IApplicationContext applicationContext) {
        Arguments arguments = Arguments.parse(applicationContext);
        Map<String, String> result = new HashMap<>();
        result.put("backend", "efinder");
        result.put("ecore", arguments.ecore.toAbsolutePath().toString());
        result.put("check", arguments.check.context() + "::" + arguments.check.constraint());
        String phase = "prepare";
        try {
            Files.createDirectories(arguments.outDir);
            EcoreCounterexamplePreparer.PreparedModel prepared = EcoreCounterexamplePreparer.prepare(
                    arguments.ecore, arguments.outDir, arguments.check, arguments.constraints);
            if (arguments.constraints != null) {
                result.put("constraints", arguments.constraints.toAbsolutePath().toString());
            }
            result.put("prepared_ecore", prepared.ecore().toString());
            result.put("generated_negation", prepared.generatedConstraint());
            result.put("verification_formula", prepared.verificationFormula());
            if (!prepared.normalizedFeatures().isEmpty()) {
                result.put("normalized_features", String.join("; ", prepared.normalizedFeatures()));
            }
            if (!prepared.abstractedFeatures().isEmpty()) {
                result.put("abstracted_features", String.join("; ", prepared.abstractedFeatures()));
            }
            phase = "load-ecore";
            ResourceSet resourceSet = new ResourceSetImpl();
            resourceSet.getResourceFactoryRegistry().getExtensionToFactoryMap()
                    .put("ecore", new EcoreResourceFactoryImpl());
            resourceSet.getResourceFactoryRegistry().getExtensionToFactoryMap()
                    .put("xmi", new XMIResourceFactoryImpl());
            ResourceSetImpl emfResourceSet = (ResourceSetImpl) resourceSet;
            emfResourceSet.setURIResourceMap(new HashMap<URI, Resource>());
            emfResourceSet.getURIResourceMap().put(
                    URI.createURI("platform:/plugin/org.eclipse.emf.ecore/model/Ecore.ecore"),
                    EcorePackage.eINSTANCE.eResource());
            Resource ecore = resourceSet.getResource(URI.createFileURI(prepared.ecore().toString()), true);
            EcoreUtil.resolveAll(resourceSet);
            registerPackages(resourceSet);

            phase = "initialize-ocl";
            CompleteOCLStandaloneSetup.doSetup();
            OCL ocl = OCL.newInstance(OCL.NO_PROJECTS, resourceSet);
            phase = "parse-ocl";
            ASResource asResource = ocl.ecore2as(ecore);
            parseOclExpressions(ocl, asResource.getModel());
            Model pivot = (Model) asResource.getContents().get(0);
            phase = "efinder-translation";
            String boundedContext = concreteWitnessContext(resourceSet, prepared.verificationContext());
            result.put("bounded_witness_context", boundedContext);
            IBoundsProvider bounds = new TargetClassBounds(boundedContext, arguments.scope,
                    arguments.referenceScope);
            UseMvFinder finder = new UseMvFinder()
                    .withBoundsProvider(bounds)
                    .withTimeOut(arguments.timeoutMillis);
            phase = "solver";
            Result finding = EFinderRunner.withOclModel(pivot).withFinder(finder).find();

            Status status = finding.getStatus();
            result.put("status", status.name());
            if (status == Status.SAT) {
                Path witness = arguments.outDir.resolve(arguments.stem() + ".counterexample.xmi");
                saveWitness(finding, witness);
                result.put("counterexample_file", witness.toAbsolutePath().toString());
            } else if (finding instanceof EFinderRunner.UnsupportedTranslationResult translation) {
                result.put("detail", translation.getReason());
            } else if (finding instanceof UseMvResult.Unsupported unsupported) {
                result.put("detail", unsupported.getReport().getUnsupported().stream()
                        .map(item -> item.getReason() == null ? "unsupported feature" : item.getReason())
                        .reduce((left, right) -> left + "; " + right).orElse("unsupported feature"));
            } else if (finding instanceof UseMvResult.UnsupportedTranslation translation) {
                result.put("detail", translation.getUseErrors());
            }
        } catch (EcoreCounterexamplePreparer.UnsupportedFeatureException exception) {
            result.put("status", "UNSUPPORTED_FEATURE");
            result.put("phase", phase);
            result.put("detail", exception.getMessage());
        } catch (Throwable exception) {
            result.put("status", diagnosticStatus(phase, exception));
            result.put("phase", phase);
            result.put("detail", exceptionDetail(exception));
        }
        writeResult(arguments.resultJson, result);
        System.out.println(toJson(result));
        // The machine-readable status is the contract with the Python wrapper.
        // Eclipse itself completed normally even when the solver reports UNSAT
        // or an unsupported OCL feature.
        return EXIT_OK;
    }

    @Override
    public void stop() {
        // The EFinder API owns no persistent process for a single finding run.
    }

    private static void registerPackages(ResourceSet resourceSet) {
        for (Resource resource : resourceSet.getResources()) {
            resource.getAllContents().forEachRemaining(object -> {
                if (object instanceof EPackage ePackage) {
                    resourceSet.getPackageRegistry().put(ePackage.getNsURI(), ePackage);
                }
            });
        }
    }

    private static void parseOclExpressions(OCL ocl, EObject object) throws Exception {
        if (object instanceof ExpressionInOCL expression) ocl.parseSpecification(expression);
        for (EObject child : object.eContents()) parseOclExpressions(ocl, child);
    }

    /**
     * An invariant on an abstract target context still describes its concrete
     * descendants, but a lower bound on the abstract class cannot create a
     * witness. Select one concrete descendant so NOT Post_i cannot be
     * satisfied vacuously with an empty target domain.
     */
    private static String concreteWitnessContext(ResourceSet resourceSet, String context) {
        List<EClass> classifiers = new ArrayList<>();
        for (Resource resource : resourceSet.getResources()) {
            resource.getAllContents().forEachRemaining(object -> {
                if (object instanceof EClass eClass) classifiers.add(eClass);
            });
        }
        EClass selected = classifiers.stream()
                .filter(eClass -> context.equals(eClass.getName()))
                .findFirst().orElse(null);
        if (selected == null || !selected.isAbstract()) return context;
        return classifiers.stream()
                .filter(eClass -> !eClass.isAbstract()
                        && eClass.getEAllSuperTypes().contains(selected))
                .map(EClass::getName)
                .findFirst().orElse(context);
    }

    private static String diagnosticStatus(String phase, Throwable exception) {
        if (exception instanceof NoClassDefFoundError || exception instanceof ClassNotFoundException
                || exception.getClass().getName().contains("BundleException")) {
            return "RUNTIME_DEPENDENCY_ERROR";
        }
        if ("parse-ocl".equals(phase) || "initialize-ocl".equals(phase)) return "OCL_PARSE_ERROR";
        if ("efinder-translation".equals(phase)) return "EFINDER_TRANSLATION_ERROR";
        if ("solver".equals(phase)) return "SOLVER_ERROR";
        return "ERROR";
    }

    private static String exceptionDetail(Throwable exception) {
        Throwable root = exception;
        while (root.getCause() != null && root.getCause() != root) root = root.getCause();
        String message = exception.getMessage() == null ? "" : exception.getMessage();
        String rootMessage = root.getMessage() == null ? "" : root.getMessage();
        return "exception=" + exception.getClass().getName() + "; message=" + message
                + "; rootCause=" + root.getClass().getName() + "; rootMessage=" + rootMessage;
    }

    private static void saveWitness(Result result, Path witness) throws IOException {
        Resource resource = result.getWitness().getResource();
        Map<String, Object> options = new HashMap<>();
        options.put(XMIResource.OPTION_SCHEMA_LOCATION, Boolean.TRUE);
        try (OutputStream output = Files.newOutputStream(witness)) {
            resource.save(output, options);
        }
    }

    private static void writeResult(Path target, Map<String, String> values) {
        try {
            Files.createDirectories(target.getParent());
            Files.writeString(target, toJson(values) + System.lineSeparator(), StandardCharsets.UTF_8);
        } catch (IOException exception) {
            throw new IllegalStateException("Cannot write result JSON: " + target, exception);
        }
    }

    private static String toJson(Map<String, String> values) {
        StringBuilder json = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, String> entry : values.entrySet()) {
            if (!first) json.append(',');
            first = false;
            json.append('\"').append(escape(entry.getKey())).append("\":\"")
                    .append(escape(entry.getValue())).append('\"');
        }
        return json.append('}').toString();
    }

    private static String escape(String value) {
        if (value == null) return "";
        return value.replace("\\", "\\\\").replace("\"", "\\\"")
                .replace("\n", "\\n").replace("\r", "\\r");
    }

    private record TargetClassBounds(String selectedClass, int objectMaximum, int referenceMaximum)
            implements IBoundsProvider {
        @Override public Interval getScope(EClass klass) {
            return new Interval(klass.getName().equals(selectedClass) ? 1 : 0, objectMaximum);
        }
        @Override public Interval getScope(EReference reference) {
            return new Interval(0, referenceMaximum);
        }
        @Override public int getDefaultMaxScope() { return objectMaximum; }
        @Override public boolean incrementScope() { return false; }
    }

    private record Arguments(Path ecore, EcoreCounterexamplePreparer.Check check, Path outDir,
                             Path resultJson, Path constraints, int scope, int referenceScope, int timeoutMillis) {
        @SuppressWarnings("unchecked")
        static Arguments parse(IApplicationContext context) {
            Object raw = context.getArguments().get(IApplicationContext.APPLICATION_ARGS);
            String[] values = raw instanceof String[] array ? array : new String[0];
            Map<String, String> options = new HashMap<>();
            for (int i = 0; i < values.length; i++) {
                if (values[i].startsWith("--") && i + 1 < values.length) options.put(values[i], values[++i]);
            }
            Path ecore = path(options, "--ecore");
            EcoreCounterexamplePreparer.Check check = EcoreCounterexamplePreparer.Check.parse(required(options, "--check"));
            Path outDir = path(options, "--out-dir");
            Path resultJson = path(options, "--result-json");
            Path constraints = optionalPath(options, "--constraints");
            return new Arguments(ecore, check, outDir, resultJson, constraints,
                    integer(options, "--scope", 3), integer(options, "--reference-scope", 6),
                    integer(options, "--timeout-ms", 300_000));
        }
        private static Path path(Map<String, String> options, String name) { return Path.of(required(options, name)); }
        private static Path optionalPath(Map<String, String> options, String name) {
            String value = options.get(name);
            return value == null || value.isBlank() ? null : Path.of(value);
        }
        private static String required(Map<String, String> options, String name) {
            String value = options.get(name);
            if (value == null || value.isBlank()) throw new IllegalArgumentException("Missing argument " + name);
            return value;
        }
        private static int integer(Map<String, String> options, String name, int fallback) {
            return Integer.parseInt(options.getOrDefault(name, Integer.toString(fallback)));
        }
        String stem() {
            String filename = ecore.getFileName().toString().replaceFirst("(?i)\\.ecore$", "");
            return filename + "__" + EcoreCounterexamplePreparer.sanitize(check.context()) + "__"
                    + EcoreCounterexamplePreparer.sanitize(check.constraint());
        }
    }
}
