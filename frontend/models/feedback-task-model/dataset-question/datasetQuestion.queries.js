import { DatasetQuestion as DatasetQuestionModel } from "./DatasetQuestion.model";

// UPSERT
const upsertDatasetQuestions = (globalQuestions) => {
  DatasetQuestionModel.insertOrUpdate({ data: globalQuestions });
};

// GET
const getQuestionsByDatasetId = (
  datasetId,
  orderBy = "order",
  ascendent = true
) => {
  const direction = ascendent ? "asc" : "desc";

  return DatasetQuestionModel.query()
    .where("dataset_id", datasetId)
    .orderBy(orderBy, direction)
    .get();
};
const getComponentTypeOfQuestionByDatasetIdAndQuestionName = (
  datasetId,
  questionName
) =>
  DatasetQuestionModel.query()
    .where("dataset_id", datasetId)
    .where("name", questionName)
    .first()?.component_type;

const getOptionsOfQuestionByDatasetIdAndQuestionName = (
  datasetId,
  questionName
) =>
  DatasetQuestionModel.query()
    .where("dataset_id", datasetId)
    .where("name", questionName)
    .first()?.options;

export {
  upsertDatasetQuestions,
  getQuestionsByDatasetId,
  getComponentTypeOfQuestionByDatasetIdAndQuestionName,
  getOptionsOfQuestionByDatasetIdAndQuestionName,
};
