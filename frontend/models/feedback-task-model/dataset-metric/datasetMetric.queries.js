import { DatasetMetric as DatasetMetricModel } from "./DatasetMetric.model";

// UPSERT
const upsertDatasetMetrics = (datasetMetrics) => {
  DatasetMetricModel.insertOrUpdate({ data: datasetMetrics });
};

// GET
const getDatasetMetricsByDatasetIdAndUser = ({ userId, datasetId }) =>
  DatasetMetricModel.query().whereId([userId, datasetId]).first();

//EXISTS
const isDatasetExistsByDatasetIdAndUserId = ({ userId, datasetId }) =>
  DatasetMetricModel.query().whereId([userId, datasetId]).exists();

export {
  upsertDatasetMetrics,
  getDatasetMetricsByDatasetIdAndUser,
  isDatasetExistsByDatasetIdAndUserId,
};
