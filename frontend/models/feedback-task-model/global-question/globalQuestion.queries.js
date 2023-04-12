import { GlobalQuestion as GlobalQuestionModel } from "../global-question/GlobalQuestion.model";

// UPSERT
const upsertGlobalQuestion = (globalQuestion) => {
  GlobalQuestionModel.insertOrUpdate({ data: globalQuestion });
};

export { upsertGlobalQuestion };
