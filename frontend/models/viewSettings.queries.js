import { DatasetViewSettings as ViewSettingsModel } from "@/models/DatasetViewSettings";

const getViewSettingsWithPaginationByDatasetName = (datasetName) =>
  ViewSettingsModel.query().with("pagination").whereId(datasetName).first();

export { getViewSettingsWithPaginationByDatasetName };
