import { TextClassificationDataset } from "@/models/TextClassification";

const getTextClassificationDatasetById = (datasetId) =>
  TextClassificationDataset.query().whereId(datasetId).first();

const getTextClassificationDatasetWithViewSettingsById = (datasetId) =>
  TextClassificationDataset.query()
    .with("viewSettings")
    .whereId(datasetId)
    .first();

export {
  getTextClassificationDatasetById,
  getTextClassificationDatasetWithViewSettingsById,
};
