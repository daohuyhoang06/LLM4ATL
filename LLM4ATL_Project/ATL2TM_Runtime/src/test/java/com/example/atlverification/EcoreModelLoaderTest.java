package com.example.atlverification;

import static org.junit.jupiter.api.Assertions.assertNotNull;

import org.junit.jupiter.api.Test;

class EcoreModelLoaderTest {

    @Test
    void loaderCanBeConstructed() {
        assertNotNull(new EcoreModelLoader());
    }
}
