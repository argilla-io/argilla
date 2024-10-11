import { availableFieldTypes } from "~/v1/domain/entities/hub/FieldCreation";
import { availableQuestionTypes } from "~/v1/domain/entities/hub/QuestionCreation";

export const useDatasetConfigurationForm = () => {
  return {
    availableFieldTypes,
    availableQuestionTypes,
  };
};
