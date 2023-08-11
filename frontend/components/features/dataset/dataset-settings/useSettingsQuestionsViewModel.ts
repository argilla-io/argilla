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

  const getDisplayTextType = (question: Question) => {
    if (question.isTextType) {
      return "Text";
    } else if (question.isRankingType) {
      return "Ranking";
    } else if (question.isRatingType) {
      return "Rating";
    } else if (question.isSingleLabelType) {
      return "Label";
    } else if (question.isMultiLabelType) {
      return "Multi-label";
    }
  };

  return {
    restore,
    update,
    getDisplayTextType,
  };
};
