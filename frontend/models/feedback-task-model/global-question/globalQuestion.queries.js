import { GlobalQuestion as GlobalQuestionModel } from "../global-question/GlobalQuestion.model";

// UPSERT
const upsertGlobalQuestion = (globalQuestion) => {
  GlobalQuestionModel.insertOrUpdate({ data: globalQuestion });
};

const upsertGlobalQuestions = (globalQuestions) => {
  GlobalQuestionModel.insertOrUpdate({ data: globalQuestions });
};

// GET
const getQuestionsByDatasetId = (
  datasetId,
  orderBy = "order",
  ascendent = true
) => {
  const direction = ascendent ? "asc" : "desc";

  return GlobalQuestionModel.query()
    .where("dataset_id", datasetId)
    .orderBy(orderBy, direction)
    .get();
};

export { upsertGlobalQuestion, upsertGlobalQuestions, getQuestionsByDatasetId };
