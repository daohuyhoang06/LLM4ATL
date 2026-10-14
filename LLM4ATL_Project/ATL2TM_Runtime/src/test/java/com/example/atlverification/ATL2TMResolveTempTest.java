package com.example.atlverification;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Path;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EPackage;
import org.junit.jupiter.api.Test;

class ATL2TMResolveTempTest {
    private static final Path FIXTURE = Path.of("src", "test", "resources");
    private static final Path ATL2TM = Path.of("..", "Neuro_Symbolic_Pipeline",
            "pipeline", "formal_verification", "hot-atl2tm", "ATL2TM.generated.atl");
    private static final String PIVOT = "http://www.eclipse.org/emf/2002/Ecore/OCL/Pivot";

    @Test
    void selectsNamedSecondaryOutputInsteadOfDefaultOutput() throws Exception {
        Path output = transform("named-output.atl", "named-output");
        EPackage model = new EcoreModelLoader().load(output);
        EClass trace = assertInstanceOf(EClass.class, model.getEClassifier("Box2Box"));
        String binding = trace.getEAnnotation(PIVOT).getDetails()
                .get("bind_Box2Box_t_tag1");
        assertEquals("self.t.tag1 = (self.s.item).oclAsType(Item).Item2Tag_s.secondary",
                binding);
        EClass producer = assertInstanceOf(EClass.class, model.getEClassifier("Item2Tag"));
        assertEquals("Tag", producer.getEStructuralFeature("secondary")
                .getEType().getName());
    }

    @Test
    void missingNamedOutputFailsClosed() {
        String message = assertThrows(ATL2TMRunner.UnsupportedAtlConstructException.class,
                () -> transform("unknown-output.atl", "unknown-output"))
                .getMessage();
        assertTrue(message.contains("__ATL2TM_UNSUPPORTED_FEATURE__RESOLVE_TEMP__"),
                message);
    }

    @Test
    void collectResolveTempSelectsNamedOutputFromTraceCollection() throws Exception {
        Path work = Path.of("target", "resolve-temp-collect-named-output");
        Path output = work.resolve("tm.ecore");
        new ATL2TMRunner().run(
                FIXTURE.resolve("resolve-temp/collect-named-output.atl"),
                FIXTURE.resolve("ordinary-lazy/collect-src.ecore"),
                FIXTURE.resolve("ordinary-lazy/collect-tgt.ecore"),
                ATL2TM, work, output);
        EPackage model = new EcoreModelLoader().load(output);
        EClass trace = assertInstanceOf(EClass.class, model.getEClassifier("Box2Box"));
        String binding = trace.getEAnnotation(PIVOT).getDetails()
                .get("bind_Box2Box_t_tags");
        assertTrue(binding.contains("Item2Tag.allInstances()"), binding);
        assertTrue(binding.contains("->collect(z | z.secondary)"), binding);
        assertTrue(binding.contains("->asSet()"), binding);
    }

    @Test
    void bibTeXCollectResolveTempUsesAllNamedFilteredRuleTraces() throws Exception {
        Path project = Path.of("..", "Neuro_Symbolic_Pipeline");
        Path work = Path.of("target", "resolve-temp-bibtex");
        Path output = work.resolve("tm.ecore");
        new ATL2TMRunner().run(
                project.resolve("ouput/final_responses/atl/BibTeX2DocBook_All.atl"),
                project.resolve("input/ATL_metamodel/BibTeX.ecore"),
                project.resolve("input/ATL_metamodel/DocBook.ecore"),
                ATL2TM, work, output);
        EPackage model = new EcoreModelLoader().load(output);
        EClass main = assertInstanceOf(EClass.class, model.getEClassifier("Main"));
        var details = main.getEAnnotation(PIVOT).getDetails();
        assertTrue(details.get("bind_Main_s1_paras").contains("UntitledEntry.allInstances()"));
        assertTrue(details.get("bind_Main_s1_paras").contains("Article_Title_Journal.allInstances()"));
        assertTrue(details.get("bind_Main_s2_paras").contains("Author__trace.allInstances()"));
        assertTrue(details.get("bind_Main_s2_paras").contains("Author__source.allInstances()"));
        assertTrue(details.get("bind_Main_s3_paras").contains("p_title"));
        assertTrue(details.get("bind_Main_s4_paras").contains("p_journal"));
        EClass titled = assertInstanceOf(EClass.class,
                model.getEClassifier("TitledEntry_Title_NoArticle"));
        assertTrue(!titled.getEAnnotation(PIVOT).getDetails()
                .get("bind_TitledEntry_Title_NoArticle_p_content")
                .contains("buildEntryPara"));
    }

    private static Path transform(String atl, String workName) throws Exception {
        Path work = Path.of("target", "resolve-temp-" + workName);
        Path output = work.resolve("tm.ecore");
        new ATL2TMRunner().run(FIXTURE.resolve("resolve-temp").resolve(atl),
                FIXTURE.resolve("ordinary-lazy/src.ecore"),
                FIXTURE.resolve("ordinary-lazy/tgt.ecore"), ATL2TM, work, output);
        return output;
    }
}
