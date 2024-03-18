import { Question } from "~/v1/domain/entities/question/Question";

export const useQuestionsViewModel = ({
  questions,
}: {
  questions: Question[];
}) => {
  const enableSpanQuestionShortcuts =
    questions.filter((q) => q.isSpanType).length === 1;

  return { enableSpanQuestionShortcuts };
};
