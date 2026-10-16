/*
 * Copyright (c) 2026.
 * SPDX-License-Identifier: EPL-2.0
 */

/** Non-interactive options for the AgileUML DSS search. */
public final class DssOptions
{
  public int sourceFeatureChainLength = 2;
  public int targetFeatureChainLength = 2;
  public boolean exactTypeMatch = false;
  public long maxCandidateMappings = 1000000L;
  public String reviewMode = "none";
  public boolean checkTargetFeatureCompleteness = false;

  public void validate()
  {
    if (sourceFeatureChainLength < 1 || sourceFeatureChainLength > 10)
    { throw new IllegalArgumentException(
        "source feature-chain length must be between 1 and 10"); }
    if (targetFeatureChainLength < 1 || targetFeatureChainLength > 10)
    { throw new IllegalArgumentException(
        "target feature-chain length must be between 1 and 10"); }
    if (maxCandidateMappings < 1)
    { throw new IllegalArgumentException("max candidate mappings must be positive"); }
    if (!("none".equals(reviewMode) || "accept".equals(reviewMode) ||
          "reject".equals(reviewMode)))
    { throw new IllegalArgumentException(
        "review mode must be none, accept, or reject"); }
  }
}
