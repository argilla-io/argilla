import { GlobalQuestion as GlobalQuestionModel } from "../global-question/GlobalQuestion.model";

// UPSERT
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

export { upsertGlobalQuestions, getQuestionsByDatasetId };
