import { GlobalLabel as GlobalLabelModel } from "./GlobalLabel.model";

const upsertLabelsInGlobalLabelModel = (labels) => {
  GlobalLabelModel.insertOrUpdate({
    data: labels,
  });
};
const deleteAllGlobalLabelModel = () => {
  GlobalLabelModel.deleteAll();
};

export { upsertLabelsInGlobalLabelModel, deleteAllGlobalLabelModel };
