package com.example.atlverification;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import java.nio.file.Path;
import java.util.Objects;

import org.eclipse.emf.ecore.EAnnotation;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EDataType;
import org.eclipse.emf.ecore.EEnum;
import org.eclipse.emf.ecore.EPackage;
import org.junit.jupiter.api.Test;

class ATL2TMEnumDataTypeTest {

    @Test
    void copiesEnumsAndCustomDataTypesIntoTransformationModel() throws Exception {
        Path fixture = Path.of("src", "test", "resources", "enum-datatype");
        Path workDir = Path.of("target", "enum-datatype-test-work");
        Path output = workDir.resolve("enum-datatype_TM.ecore");
        Path atl2tm = Path.of(
                "..",
                "Neuro-Symbolic Pipeline",
                "pipeline",
                "formal_verification",
                "atl",
                "transformations",
                "ATL2TM.atl"
        );

        new ATL2TMRunner().run(
                fixture.resolve("EnumDataType.atl"),
                fixture.resolve("src.ecore"),
                fixture.resolve("tgt.ecore"),
                atl2tm,
                workDir,
                output
        );

        EPackage transformationModel = new EcoreModelLoader().load(output);

        EAnnotation modelProvenance = annotation(
                transformationModel,
                "urn:llm4atl:provenance"
        );
        assertEquals("1", modelProvenance.getDetails().get("schemaVersion"));
        assertEquals("EnumDataType", modelProvenance.getDetails().get("atlModule"));

        EEnum sourceKind = assertInstanceOf(
                EEnum.class,
                transformationModel.getEClassifier("SourceKind")
        );
        assertEquals(2, sourceKind.getELiterals().size());
        assertEquals("first", sourceKind.getELiterals().get(0).getLiteral());
        assertEquals("second", sourceKind.getELiterals().get(1).getLiteral());

        EDataType sourceCode = assertInstanceOf(
                EDataType.class,
                transformationModel.getEClassifier("SourceCode")
        );
        assertEquals("java.lang.String", sourceCode.getInstanceClassName());

        EClass source = assertInstanceOf(
                EClass.class,
                transformationModel.getEClassifier("Source")
        );
        assertEquals(
                sourceKind,
                source.getEStructuralFeature("kind").getEType()
        );
        assertEquals(
                sourceCode,
                source.getEStructuralFeature("code").getEType()
        );
        assertEquals(
                "source",
                annotation(source, "urn:llm4atl:provenance")
                        .getDetails().get("origin")
        );
        assertEquals(
                "sourceInvariant",
                annotation(source, "urn:llm4atl:provenance")
                        .getDetails().get("preConstraints")
        );
        assertEquals(
                "Source2Result",
                annotation(source, "urn:llm4atl:provenance")
                        .getDetails().get("atlRules")
        );
        assertEquals(
                "match_Source2Result",
                annotation(source, "urn:llm4atl:provenance")
                        .getDetails().get("semConstraints")
        );

        EEnum targetKind = assertInstanceOf(
                EEnum.class,
                transformationModel.getEClassifier("TargetKind")
        );
        assertEquals(
                "target",
                annotation(targetKind, "urn:llm4atl:provenance")
                        .getDetails().get("origin")
        );

        EClass result = assertInstanceOf(
                EClass.class,
                transformationModel.getEClassifier("Result")
        );
        assertEquals(
                "targetInvariant",
                annotation(result, "urn:llm4atl:provenance")
                        .getDetails().get("postConstraints")
        );
        assertEquals(
                "Source2Result",
                annotation(result, "urn:llm4atl:provenance")
                        .getDetails().get("atlRules")
        );
        assertEquals(
                "create_Result",
                annotation(result, "urn:llm4atl:provenance")
                        .getDetails().get("semConstraints")
        );

        EDataType targetCode = assertInstanceOf(
                EDataType.class,
                transformationModel.getEClassifier("TargetCode")
        );
        assertEquals(
                "target",
                annotation(targetCode, "urn:llm4atl:provenance")
                        .getDetails().get("origin")
        );

        EClass trace = assertInstanceOf(
                EClass.class,
                transformationModel.getEClassifier("Source2Result")
        );
        EAnnotation traceProvenance = annotation(
                trace,
                "urn:llm4atl:provenance"
        );
        assertEquals("trace", traceProvenance.getDetails().get("origin"));
        assertEquals("Source2Result", traceProvenance.getDetails().get("atlRule"));

        assertNotNull(targetCode);
    }

    private static EAnnotation annotation(
            org.eclipse.emf.ecore.EModelElement element,
            String source
    ) {
        return element.getEAnnotations().stream()
                .filter(a -> Objects.equals(source, a.getSource()))
                .findFirst()
                .orElseThrow(() -> new AssertionError(
                        "Missing annotation: " + source
                ));
    }
}
