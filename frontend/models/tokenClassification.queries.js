import { TokenClassificationDataset } from "@/models/TokenClassification";

const getTokenClassificationDatasetById = (datasetId) =>
  TokenClassificationDataset.query().whereId(datasetId).first();

const getTokenClassificationDatasetWithViewSettingsById = (datasetId) =>
  TokenClassificationDataset.query()
    .with("viewSettings")
    .whereId(datasetId)
    .first();

export {
  getTokenClassificationDatasetById,
  getTokenClassificationDatasetWithViewSettingsById,
};
