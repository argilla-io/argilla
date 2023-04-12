import { GlobalQuestion as GlobalQuestionModel } from "../global-question/GlobalQuestion.model";

// UPSERT
const upsertGlobalQuestion = (globalQuestion) => {
  GlobalQuestionModel.insertOrUpdate({ data: globalQuestion });
};

const upsertGlobalQuestions = (globalQuestions) => {
  GlobalQuestionModel.insertOrUpdate({ data: globalQuestions });
};

export { upsertGlobalQuestion, upsertGlobalQuestions };
