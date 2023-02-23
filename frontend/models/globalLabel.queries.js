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

export {
  getAllLabelsByDatasetId,
  upsertLabelsInGlobalLabelModel,
  deleteAllGlobalLabelModel,
};
