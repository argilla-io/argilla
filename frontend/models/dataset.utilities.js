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

const getDatasetFromORM = (
  datasetId,
  datasetTask,
  isWithViewSettings = false
) => {
  try {
    if (isWithViewSettings)
      return getTaskDatasetWithViewSettingsById(datasetId, datasetTask);
    return getTaskDatasetById(datasetId, datasetTask);
  } catch (err) {
    console.error(err);
    return null;
  }
};

const getTaskDatasetById = (datasetId, datasetTask) => {
  let datasetById = null;
  switch (datasetTask.toUpperCase()) {
    case "TEXTCLASSIFICATION":
      datasetById = getTextClassificationDatasetById(datasetId);
      break;
    case "TOKENCLASSIFICATION":
      datasetById = getTokenClassificationDatasetById(datasetId);
      break;
    case "TEXT2TEXT":
      datasetById = getText2TextDatasetById(datasetId);
      break;
    default:
      throw new Error(`ERROR Unknown task: ${datasetTask}`);
  }
  return datasetById;
};

const getTaskDatasetWithViewSettingsById = (datasetId, datasetTask) => {
  let datasetById = null;
  switch (datasetTask.toUpperCase()) {
    case "TEXTCLASSIFICATION":
      datasetById = getTextClassificationDatasetWithViewSettingsById(datasetId);
      break;
    case "TOKENCLASSIFICATION":
      datasetById =
        getTokenClassificationDatasetWithViewSettingsById(datasetId);
      break;
    case "TEXT2TEXT":
      datasetById = getText2TextDatasetWithViewSettingsById(datasetId);
      break;
    default:
      throw new Error(`ERROR Unknown task: ${datasetTask}`);
  }
  return datasetById;
};

export { getDatasetFromORM };
