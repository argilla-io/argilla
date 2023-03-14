import { ObservationDataset } from "@/models/Dataset";
import {
  getTokenClassificationDatasetById,
  getTokenClassificationDatasetWithViewSettingsById,
} from "@/models/tokenClassification.queries";
import {
  getTextClassificationDatasetById,
  getTextClassificationDatasetWithViewSettingsById,
} from "@/models/textClassification.queries";
import {
  getText2TextDatasetById,
  getText2TextDatasetWithViewSettingsById,
} from "@/models/text2text.queries";

const getDatasetTaskById = (datasetId) => {
  return ObservationDataset.query().whereId(datasetId).first()?.task || null;
};

const getDatasetFromORM = (
  datasetId,
  datasetTask,
  isWithViewSettings = false
) => {
  try {
    return getTaskDatasetById(datasetId, datasetTask, isWithViewSettings);
  } catch (err) {
    console.error(err);
    return null;
  }
};

const getTaskDatasetById = (datasetId, datasetTask, isWithViewSettings) => {
  let datasetById = null;
  switch (datasetTask.toUpperCase()) {
    case "TEXTCLASSIFICATION":
      datasetById = isWithViewSettings
        ? getTextClassificationDatasetWithViewSettingsById(datasetId)
        : getTextClassificationDatasetById(datasetId);
      break;
    case "TOKENCLASSIFICATION":
      datasetById = isWithViewSettings
        ? getTokenClassificationDatasetWithViewSettingsById(datasetId)
        : getTokenClassificationDatasetById(datasetId);
      break;
    case "TEXT2TEXT":
      datasetById = isWithViewSettings
        ? getText2TextDatasetWithViewSettingsById(datasetId)
        : getText2TextDatasetById(datasetId);
      break;
    default:
      throw new Error(`ERROR Unknown task: ${datasetTask}`);
  }
  return datasetById;
};

export { getDatasetFromORM, getDatasetTaskById };
