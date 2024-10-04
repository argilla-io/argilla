import {
  availableFieldTypes,
  availableMetadataType,
  availableQuestionTypes,
} from "~/v1/domain/entities/hub/DatasetCreation";

export const useDatasetConfigurationForm = () => {
  return {
    availableFieldTypes,
    availableMetadataType,
    availableQuestionTypes,
  };
};
