import { Text2TextDataset } from "@/models/Text2Text";

const getText2TextDatasetById = (datasetId) =>
  Text2TextDataset.query().whereId(datasetId).first();

export { getText2TextDatasetById };
