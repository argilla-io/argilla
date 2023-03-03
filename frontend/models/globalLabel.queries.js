import {
  GlobalLabel as GlobalLabelModel,
  formatDatasetIdForGlobalLabelModel,
} from "./GlobalLabel.model";

const upsertLabelsInGlobalLabelModel = (labels) => {
  GlobalLabelModel.insertOrUpdate({
    data: labels,
  });
};
const deleteAllGlobalLabelModel = () => {
  GlobalLabelModel.deleteAll();
};

const getAllLabelsByDatasetId = (datasetId, sortBy = "order", asc = true) => {
  const directionSort = asc ? "asc" : "desc";
  const joinedDatasetId = formatDatasetIdForGlobalLabelModel(datasetId);
  const labels = GlobalLabelModel.query()
    .where("dataset_id", joinedDatasetId)
    .orderBy(sortBy, directionSort)
    .get();

  return labels;
};

const getAllLabelsTextByDatasetId = (
  datasetId,
  sortBy = "order",
  asc = true
) => {
  return getAllLabelsByDatasetId(datasetId, sortBy, asc).reduce(
    (acc, curr) => acc.concat(curr.text),
    []
  );
};

const countLabelsByDatasetId = (datasetId) => {
  const joinedDatasetId = formatDatasetIdForGlobalLabelModel(datasetId);
  const numberOfLabels = GlobalLabelModel.query()
    .where("dataset_id", joinedDatasetId)
    .count();

  return numberOfLabels;
};

const upsertNewGlobalLabel = ({
  datasetId,
  newLabel,
  isActivate = false,
  isSavedInBack = false,
}) => {
  const joinedDatasetId = formatDatasetIdForGlobalLabelModel(datasetId);
  const numberOfLabels = countLabelsByDatasetId(datasetId);

  GlobalLabelModel.insertOrUpdate({
    data: {
      text: newLabel,
      dataset_id: joinedDatasetId,
      order: numberOfLabels,
      color_id: numberOfLabels,
      shortcut: numberOfLabels < 9 ? String(numberOfLabels + 1) : null,
      is_activate: isActivate,
      is_saved_in_back: isSavedInBack,
    },
  });
};

const getLabelsNotSavedInBackByDatasetId = (datasetId, sortBy = "order") => {
  const joinedDatasetId = formatDatasetIdForGlobalLabelModel(datasetId);
  const labels = GlobalLabelModel.query()
    .where("dataset_id", joinedDatasetId)
    .where("is_saved_in_back", false)
    .orderBy(sortBy)
    .get();

  return labels;
};

const isExistAnyLabelsNotSavedInBackByDatasetId = (datasetId) => {
  const joinedDatasetId = formatDatasetIdForGlobalLabelModel(datasetId);
  const isAnyLabels = GlobalLabelModel.query()
    .where("dataset_id", joinedDatasetId)
    .where("is_saved_in_back", false)
    .exists();

  return isAnyLabels;
};

const isLabelTextExistInGlobalLabel = (datasetId, labelText) => {
  const joinedDatasetId = formatDatasetIdForGlobalLabelModel(datasetId);

  const compareValueToLabelText = (value) => value === labelText;

  return GlobalLabelModel.query()
    .where("dataset_id", joinedDatasetId)
    .where("text", compareValueToLabelText)
    .exists();
};

const isLabelTextExistInGlobalLabelAndSavedInBack = (datasetId, labelText) => {
  const joinedDatasetId = formatDatasetIdForGlobalLabelModel(datasetId);

  const compareValueToLabelText = (value) => value === labelText;

  return GlobalLabelModel.query()
    .where("dataset_id", joinedDatasetId)
    .where("text", compareValueToLabelText)
    .where("is_saved_in_back", true)
    .exists();
};

const getTotalLabelsInGlobalLabel = (datasetId) => {
  const joinedDatasetId = formatDatasetIdForGlobalLabelModel(datasetId);
  return GlobalLabelModel.query().where("dataset_id", joinedDatasetId).get()
    .length;
};

export {
  getAllLabelsByDatasetId,
  getLabelsNotSavedInBackByDatasetId,
  isExistAnyLabelsNotSavedInBackByDatasetId,
  upsertLabelsInGlobalLabelModel,
  deleteAllGlobalLabelModel,
  upsertNewGlobalLabel,
  getAllLabelsTextByDatasetId,
  isLabelTextExistInGlobalLabel,
  isLabelTextExistInGlobalLabelAndSavedInBack,
  getTotalLabelsInGlobalLabel,
};
