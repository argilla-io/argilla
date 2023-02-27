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

const insertNewGlobalLabel = ({ datasetId, newLabel, isActivate = false }) => {
  const joinedDatasetId = formatDatasetIdForGlobalLabelModel(datasetId);
  const numberOfLabels = countLabelsByDatasetId(datasetId);
  GlobalLabelModel.insert({
    data: {
      id: newLabel,
      text: newLabel,
      dataset_id: joinedDatasetId,
      order: numberOfLabels,
      color_id: numberOfLabels,
      shortcut: numberOfLabels < 9 ? String(numberOfLabels + 1) : null,
      is_activate: isActivate,
    },
  });
};

const isLabelTextExistInGlobalLabel = (datasetId, labelText) => {
  const joinedDatasetId = formatDatasetIdForGlobalLabelModel(datasetId);

  const compareWithCaseInsensitive = (value) =>
    value.toUpperCase() === labelText.toUpperCase();

  return GlobalLabelModel.query()
    .where("dataset_id", joinedDatasetId)
    .where("text", compareWithCaseInsensitive)
    .exists();
};

export {
  getAllLabelsByDatasetId,
  upsertLabelsInGlobalLabelModel,
  deleteAllGlobalLabelModel,
  insertNewGlobalLabel,
  getAllLabelsTextByDatasetId,
  isLabelTextExistInGlobalLabel,
};
