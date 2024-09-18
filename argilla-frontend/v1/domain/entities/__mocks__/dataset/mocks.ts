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
    "",
    "",
    ""
  );
};
