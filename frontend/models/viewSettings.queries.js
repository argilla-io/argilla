import { DatasetViewSettings as ViewSettingsModel } from "@/models/DatasetViewSettings";

const getViewSettingsWithPaginationByDatasetName = (datasetName) =>
  ViewSettingsModel.query().with("pagination").whereId(datasetName).first();

const getViewSettingsByDatasetName = (datasetName) =>
  ViewSettingsModel.query().whereId(datasetName).first();

const updateLoadingState = (datasetName, loadingValue) => {
  ViewSettingsModel.update({
    where: datasetName,
    data: { loading: loadingValue },
  });
};

const getLoadingValue = (datasetName) => {
  return ViewSettingsModel.query().whereId(datasetName).first();
};

const getShortcutChars = (datasetName) => {
  return (
    ViewSettingsModel.query().whereId(datasetName).first()?.shortcut_chars ?? ""
  );
};

export {
  getViewSettingsWithPaginationByDatasetName,
  getViewSettingsByDatasetName,
  getLoadingValue,
  updateLoadingState,
  getShortcutChars,
};
