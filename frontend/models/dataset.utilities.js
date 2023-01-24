import { getTokenClassificationDatasetById } from "@/models/tokenClassification.queries";
import { getTextClassificationDatasetById } from "@/models/textClassification.queries";
import { getText2TextDatasetById } from "@/models/text2text.queries";

const getDatasetFromORM = (datasetId, datasetTask) => {
  try {
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

export { getDatasetFromORM };
