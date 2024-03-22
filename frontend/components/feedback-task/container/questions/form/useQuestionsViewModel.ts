import { Question } from "~/v1/domain/entities/question/Question";

export const useQuestionsViewModel = ({
  questions,
}: {
  questions: Question[];
}) => {
  const enableSpanQuestionShortcutsGlobal =
    questions.filter((q) => q.isSpanType).length === 1;

  return { enableSpanQuestionShortcutsGlobal };
};
