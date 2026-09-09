package com.example.atlverification;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import java.nio.file.Path;

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

        assertNotNull(transformationModel.getEClassifier("TargetKind"));
        assertNotNull(transformationModel.getEClassifier("TargetCode"));
    }
}
