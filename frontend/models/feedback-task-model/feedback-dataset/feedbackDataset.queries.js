import { FeedbackDataset as FeedbackDatasetModel } from "./FeedbackDataset.model";

// UPSERT
const upsertFeedbackDataset = (feedbackDataset) => {
  FeedbackDatasetModel.insertOrUpdate({ data: feedbackDataset });
};

const updateTotalRecordsByDatasetId = (datasetId, totalRecords) => {
  FeedbackDatasetModel.update({
    where: datasetId,
    data: { total_records: totalRecords },
  });
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
const getTotalRecordByDatasetId = (datasetId) => {
  return FeedbackDatasetModel.query().whereId(datasetId).first()?.total_records;
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

export {
  upsertFeedbackDataset,
  updateTotalRecordsByDatasetId,
  getAllFeedbackDatasets,
  getFeedbackDatasetNameById,
  getDatasetGuidelinesByDatasetId,
  getDatasetTaskByDatasetId,
  getFeedbackDatasetWorkspaceNameById,
  getTotalRecordByDatasetId,
  isDatasetByIdExists,
};
