import { FeedbackDataset as FeedbackDatasetModel } from "./FeedbackDataset.model";

// UPSERT
const upsertFeedbackDataset = (feedbackDataset) => {
  FeedbackDatasetModel.insertOrUpdate({ data: feedbackDataset });
};

// GET
const getFeedbackDatasetNameById = (datasetId) => {
  return FeedbackDatasetModel.query().whereId(datasetId).first()?.name || null;
};
const getFeedbackDatasetWorkspaceNameById = (datasetId) => {
  return (
    FeedbackDatasetModel.query().whereId(datasetId).first()?.workspace_name ||
    null
  );
};
const getTotalRecordByDatasetId = (datasetId) => {
  return FeedbackDatasetModel.query().whereId(datasetId).first()?.total_records;
};

export {
  upsertFeedbackDataset,
  getFeedbackDatasetNameById,
  getFeedbackDatasetWorkspaceNameById,
  getTotalRecordByDatasetId,
};
