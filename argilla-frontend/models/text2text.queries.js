import { Text2TextDataset } from "@/models/Text2Text";

const getText2TextDatasetById = (datasetId) =>
  Text2TextDataset.query().whereId(datasetId).first();

const getText2TextDatasetWithViewSettingsById = (datasetId) =>
  Text2TextDataset.query().with("viewSettings").whereId(datasetId).first();

export { getText2TextDatasetById, getText2TextDatasetWithViewSettingsById };
