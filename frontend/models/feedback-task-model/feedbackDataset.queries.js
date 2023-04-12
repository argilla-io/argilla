import { FeedbackDataset as FeedbackDatasetModel } from "./FeedbackDataset.model";

// upsert
const upsertFeedbackDataset = (feedbackDataset) => {
  FeedbackDatasetModel.insertOrUpdate({ data: feedbackDataset });
};

// get
const getFeedbackDatasetNameById = (datasetId) => {
  return FeedbackDatasetModel.query().whereId(datasetId).first()?.name || null;
};
const getFeedbackDatasetWorkspaceNameById = (datasetId) => {
  return (
    FeedbackDatasetModel.query().whereId(datasetId).first()?.workspace_name ||
    null
  );
};

// delete

export {
  upsertFeedbackDataset,
  getFeedbackDatasetNameById,
  getFeedbackDatasetWorkspaceNameById,
};
