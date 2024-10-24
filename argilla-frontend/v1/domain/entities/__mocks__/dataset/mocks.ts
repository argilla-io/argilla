import { Dataset } from "../../dataset/Dataset";

export const createEmptyDataset = () => {
  return new Dataset(
    "FAKE_ID",
    "FAKE_NAME",
    "FAKE_GUIDELINES",
    "ready",
    "FAKE_WORKSPACE_ID",
    "FAKE_WORKSPACE_NAME",
    false,
    {
      strategy: "FAKE",
      minSubmitted: 1,
    },
    {
      repoId: "FAKE_REPO_ID",
      subset: "FAKE_SUBSET",
      split: "FAKE_SPLIT",
      mapping: {
        fields: [{ source: "FAKE_SOURCE", target: "FAKE_TARGET" }],
        metadata: [{ source: "FAKE_SOURCE", target: "FAKE_TARGET" }],
        suggestions: [{ source: "FAKE_SOURCE", target: "FAKE_TARGET" }],
      },
    },
    "",
    "",
    ""
  );
};
