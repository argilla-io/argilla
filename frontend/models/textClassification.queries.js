import { TextClassificationDataset } from "./TextClassification";

const getTextClassificationDatasetById = (datasetId) =>
  TextClassificationDataset.query().whereId(datasetId).first();

export { getTextClassificationDatasetById };
