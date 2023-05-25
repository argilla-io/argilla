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
const getDatasetTaskByDatasetId = (datasetId) => {
  return FeedbackDatasetModel.query().whereId(datasetId).first()?.task;
};
const getDatasetGuidelinesByDatasetId = (datasetId) => {
  return FeedbackDatasetModel.query().whereId(datasetId).first()?.guidelines;
};

// EXIST
const isDatasetByIdExists = (datasetId) => {
  return FeedbackDatasetModel.query().whereId(datasetId).exists();
};

// DELETE
const deleteDatasetById = (datasetId) => {
  return FeedbackDatasetModel.delete(datasetId);
};
export {
  upsertFeedbackDataset,
  getAllFeedbackDatasets,
  getFeedbackDatasetNameById,
  getDatasetGuidelinesByDatasetId,
  getDatasetTaskByDatasetId,
  getFeedbackDatasetWorkspaceNameById,
  isDatasetByIdExists,
  deleteDatasetById,
};
