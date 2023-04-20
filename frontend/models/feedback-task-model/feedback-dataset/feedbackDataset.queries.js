import { FeedbackDataset as FeedbackDatasetModel } from "./FeedbackDataset.model";

// UPSERT
const upsertFeedbackDataset = (feedbackDataset) => {
  FeedbackDatasetModel.insertOrUpdate({ data: feedbackDataset });
};

// GET
const getAllFeedbackDatasets = () => {
  return FeedbackDatasetModel.all();
};
const getFeedbackDatasetNameById = (datasetId) => {
  return FeedbackDatasetModel.query().whereId(datasetId).first()?.name || null;
};
const getFeedbackDatasetWorkspaceNameById = (datasetId) => {
  return (
    FeedbackDatasetModel.query().whereId(datasetId).first()?.workspace_name ||
    null
  );
};

export {
  upsertFeedbackDataset,
  getAllFeedbackDatasets,
  getFeedbackDatasetNameById,
  getFeedbackDatasetWorkspaceNameById,
};
