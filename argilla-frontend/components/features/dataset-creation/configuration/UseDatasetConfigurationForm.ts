import {
  availableFieldTypes,
  availableMetadataTypes,
  availableQuestionTypes,
} from "~/v1/domain/entities/hub/DatasetCreation";

export const useDatasetConfigurationForm = () => {
  return {
    availableFieldTypes,
    availableMetadataTypes,
    availableQuestionTypes,
  };
};
