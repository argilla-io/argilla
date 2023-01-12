import { TokenClassificationDataset } from "@/models/TokenClassification";

const getTokenClassificationDatasetById = (datasetId) =>
  TokenClassificationDataset.query().whereId(datasetId).first();

export { getTokenClassificationDatasetById };
