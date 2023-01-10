import { DatasetViewSettings as ViewSettingsModel } from "@/models/DatasetViewSettings";

const getViewSettingsByDatasetName = (datasetName) =>
  ViewSettingsModel.query().whereId(datasetName).first();

const getViewSettingsWithPaginationByDatasetName = (datasetName) =>
  ViewSettingsModel.query().with("pagination").whereId(datasetName).first();

export {
  getViewSettingsWithPaginationByDatasetName,
  getViewSettingsByDatasetName,
};
