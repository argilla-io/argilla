import { useResolve } from "ts-injecty";
import { Question } from "~/v1/domain/entities/question/Question";
import { UpdateQuestionSettingUseCase } from "~/v1/domain/usecases/dataset-setting/update-question-setting-use-case";

export const useSettingsQuestionsViewModel = () => {
  const updateQuestionSettingsUseCase = useResolve(
    UpdateQuestionSettingUseCase
  );

  const restore = (question: Question) => {
    question.restore();
  };

  const update = async (question: Question) => {
    try {
      await updateQuestionSettingsUseCase.execute(question);
    } catch (error) {
      // TODO
    }
  };

  return {
    restore,
    update,
  };
};
