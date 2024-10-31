import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { availableFieldTypes } from "~/v1/domain/entities/hub/FieldCreation";
import { availableQuestionTypes } from "~/v1/domain/entities/hub/QuestionCreation";
import { CreateDatasetUseCase } from "~/v1/domain/usecases/create-dataset-use-case";
import { useRoutes } from "~/v1/infrastructure/services";

export const useDatasetConfigurationForm = () => {
  const isLoading = ref(false);
  const { goToFeedbackTaskAnnotationPage } = useRoutes();
  const createDatasetUseCase = useResolve(CreateDatasetUseCase);

  const create = async (dataset) => {
    isLoading.value = true;

    try {
      const datasetId = await createDatasetUseCase.execute(dataset);

      if (!datasetId) return;

      goToFeedbackTaskAnnotationPage(datasetId);
    } finally {
      isLoading.value = false;
    }
  };

  return {
    availableFieldTypes,
    availableQuestionTypes,
    create,
    isLoading,
  };
};
