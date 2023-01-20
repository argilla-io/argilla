import { TextClassificationDataset } from "@/models/TextClassification";

const getTextClassificationDatasetById = (datasetId) =>
  TextClassificationDataset.query().whereId(datasetId).first();

export { getTextClassificationDatasetById };
