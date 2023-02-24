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

const getAllLabelsByDatasetId = (datasetId) => {
  const joinedDatasetId = formatDatasetIdForGlobalLabelModel(datasetId);
  const labels = GlobalLabelModel.query()
    .where("dataset_id", joinedDatasetId)
    .get();

  return labels;
};

const getAllLabelsTextByDatasetId = (datasetId) => {
  return getAllLabelsByDatasetId(datasetId).reduce(
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
      color_id: numberOfLabels,
      shortcurt: numberOfLabels < 10 ? String(numberOfLabels) : null,
      is_activate: isActivate,
    },
  });
};

export {
  getAllLabelsByDatasetId,
  upsertLabelsInGlobalLabelModel,
  deleteAllGlobalLabelModel,
  insertNewGlobalLabel,
  getAllLabelsTextByDatasetId,
};
