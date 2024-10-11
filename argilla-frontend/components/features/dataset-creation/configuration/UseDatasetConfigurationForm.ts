import { useResolve } from "ts-injecty";
import { availableFieldTypes } from "~/v1/domain/entities/hub/FieldCreation";
import { availableMetadataTypes } from "~/v1/domain/entities/hub/MetadataCreation";
import { availableQuestionTypes } from "~/v1/domain/entities/hub/QuestionCreation";
import { CreateDatasetUseCase } from "~/v1/domain/usecases/create-dataset-use-case";

export const useDatasetConfigurationForm = () => {
  const useCase = useResolve(CreateDatasetUseCase);

  const create = async (dataset: any) => {
    await useCase.execute(dataset);
  };

  return {
    availableFieldTypes,
    availableMetadataTypes,
    availableQuestionTypes,
    create,
  };
};
