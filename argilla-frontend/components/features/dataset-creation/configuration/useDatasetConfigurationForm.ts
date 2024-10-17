import { useResolve } from "ts-injecty";
import { availableFieldTypes } from "~/v1/domain/entities/hub/FieldCreation";
import { availableQuestionTypes } from "~/v1/domain/entities/hub/QuestionCreation";
import { CreateDatasetUseCase } from "~/v1/domain/usecases/create-dataset-use-case";
import { useRoutes } from "~/v1/infrastructure/services";

export const useDatasetConfigurationForm = () => {
  const { goToFeedbackTaskAnnotationPage } = useRoutes();
  const createDatasetUseCase = useResolve(CreateDatasetUseCase);

  const create = async (dataset: any) => {
    const datasetId = await createDatasetUseCase.execute(dataset);

    if (!datasetId) return;

    goToFeedbackTaskAnnotationPage(datasetId);
  };

  return {
    availableFieldTypes,
    availableQuestionTypes,
    create,
  };
};
