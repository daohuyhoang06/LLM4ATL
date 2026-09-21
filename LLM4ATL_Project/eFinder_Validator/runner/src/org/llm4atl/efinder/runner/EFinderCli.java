package org.llm4atl.efinder.runner;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

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
import org.eclipse.ocl.pivot.Model;
import org.eclipse.ocl.pivot.ExpressionInOCL;
import org.eclipse.ocl.pivot.resource.ASResource;
import org.eclipse.ocl.xtext.completeocl.CompleteOCLStandaloneSetup;
import org.eclipse.ocl.pivot.utilities.OCL;

import efinder.core.IBoundsProvider;
import efinder.core.IModelFinder.Result;
import efinder.core.IModelFinder.Status;
import efinder.emfocl.runner.EFinderRunner;
import efinder.usemv.UseMvFinder;
import efinder.usemv.UseMvResult;

/** Standalone Java entry point; it does not require Eclipse IDE or Equinox. */
public final class EFinderCli {
    private EFinderCli() {}

    public static void main(String[] args) {
        Arguments arguments;
        try {
            arguments = Arguments.parse(args);
        } catch (Exception exception) {
            System.err.println("EFinder argument error: " + exception.getMessage());
            System.exit(2);
            return;
        }

        Map<String, String> result = new HashMap<>();
        result.put("backend", "efinder");
        result.put("ecore", arguments.ecore.toAbsolutePath().toString());
        result.put("check", arguments.check.context() + "::" + arguments.check.constraint());
        try {
            Files.createDirectories(arguments.outDir);
            EcoreCounterexamplePreparer.PreparedModel prepared = EcoreCounterexamplePreparer.prepare(
                    arguments.ecore, arguments.outDir, arguments.check);
            result.put("prepared_ecore", prepared.ecore().toString());
            result.put("generated_negation", prepared.generatedConstraint());

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

            CompleteOCLStandaloneSetup.doSetup();
            OCL ocl = OCL.newInstance(OCL.NO_PROJECTS, resourceSet);
            ASResource asResource = ocl.ecore2as(ecore);
            parseOclExpressions(ocl, asResource.getModel());
            Model pivot = (Model) asResource.getContents().get(0);
            IBoundsProvider bounds = new TargetClassBounds(arguments.check.context(), arguments.scope,
                    arguments.referenceScope);
            UseMvFinder finder = new UseMvFinder()
                    .withBoundsProvider(bounds)
                    .withTimeOut(arguments.timeoutMillis);
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
        } catch (Exception exception) {
            result.put("status", "ERROR");
            result.put("detail", exception.getClass().getSimpleName() + ": " + exception.getMessage());
        }

        writeResult(arguments.resultJson, result);
        System.out.println(toJson(result));
        if ("ERROR".equals(result.get("status"))) System.exit(1);
    }

    private static void registerPackages(ResourceSet resourceSet) {
        for (Resource resource : resourceSet.getResources()) {
            for (java.util.Iterator<EObject> iterator = resource.getAllContents(); iterator.hasNext();) {
                EObject object = iterator.next();
                if (object instanceof EPackage ePackage && ePackage.getNsURI() != null) {
                    resourceSet.getPackageRegistry().put(ePackage.getNsURI(), ePackage);
                }
            }
        }
    }

    private static void parseOclExpressions(OCL ocl, EObject object) throws Exception {
        if (object instanceof ExpressionInOCL expression) ocl.parseSpecification(expression);
        for (EObject child : object.eContents()) parseOclExpressions(ocl, child);
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
            Files.createDirectories(target.toAbsolutePath().getParent());
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
            json.append('"').append(escape(entry.getKey())).append("\":\"")
                    .append(escape(entry.getValue())).append('"');
        }
        return json.append('}').toString();
    }

    private static String escape(String value) {
        if (value == null) return "";
        StringBuilder escaped = new StringBuilder();
        for (int i = 0; i < value.length(); i++) {
            char character = value.charAt(i);
            switch (character) {
                case '\\' -> escaped.append("\\\\");
                case '"' -> escaped.append("\\\"");
                case '\b' -> escaped.append("\\b");
                case '\f' -> escaped.append("\\f");
                case '\n' -> escaped.append("\\n");
                case '\r' -> escaped.append("\\r");
                case '\t' -> escaped.append("\\t");
                default -> {
                    if (character < 0x20) escaped.append(String.format("\\u%04x", (int) character));
                    else escaped.append(character);
                }
            }
        }
        return escaped.toString();
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
                             Path resultJson, int scope, int referenceScope, int timeoutMillis) {
        static Arguments parse(String[] args) {
            Map<String, String> options = new HashMap<>();
            for (int i = 0; i < args.length; i++) {
                if (args[i].startsWith("--") && i + 1 < args.length) options.put(args[i], args[++i]);
            }
            Path ecore = path(options, "--ecore");
            EcoreCounterexamplePreparer.Check check = EcoreCounterexamplePreparer.Check.parse(required(options, "--check"));
            Path outDir = path(options, "--out-dir");
            Path resultJson = path(options, "--result-json");
            return new Arguments(ecore, check, outDir, resultJson,
                    integer(options, "--scope", 3), integer(options, "--reference-scope", 6),
                    integer(options, "--timeout-ms", 300_000));
        }
        private static Path path(Map<String, String> options, String name) { return Path.of(required(options, name)); }
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
