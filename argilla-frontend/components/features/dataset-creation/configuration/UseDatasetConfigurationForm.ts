import { availableFieldTypes } from "~/v1/domain/entities/hub/FieldCreation";
import { availableMetadataTypes } from "~/v1/domain/entities/hub/MetadataCreation";
import { availableQuestionTypes } from "~/v1/domain/entities/hub/QuestionCreation";

export const useDatasetConfigurationForm = () => {
  return {
    availableFieldTypes,
    availableMetadataTypes,
    availableQuestionTypes,
  };
};
