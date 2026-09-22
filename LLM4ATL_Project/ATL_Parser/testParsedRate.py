#!/usr/bin/env python3
"""Compatibility entry point for the current ATL parser evaluation script.

The old version of this file belonged to the removed Reactions project and
used paths that no longer exist.  Keep the historical filename, but delegate
to the ATL-specific implementation so it follows the current repository
layout.
"""

from testATLParsedRate import generate_reports


if __name__ == "__main__":
    generate_reports()
