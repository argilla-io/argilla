import { FeedbackDataset as FeedbackDatasetModel } from "./FeedbackDataset.model";

/**
 * @deprecated
 */
const deleteDatasetById = (datasetId) => {
  return FeedbackDatasetModel.delete(datasetId);
};

export { deleteDatasetById };
