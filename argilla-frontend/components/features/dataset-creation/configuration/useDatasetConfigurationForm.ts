import { useResolve } from "ts-injecty";
import { availableFieldTypes } from "~/v1/domain/entities/hub/FieldCreation";
import { availableQuestionTypes } from "~/v1/domain/entities/hub/QuestionCreation";
import { CreateDatasetUseCase } from "~/v1/domain/usecases/create-dataset-use-case";
import { useRoutes } from "~/v1/infrastructure/services";
import { ref } from "vue-demi";

export const useDatasetConfigurationForm = () => {
  const { goToFeedbackTaskAnnotationPage } = useRoutes();
  const createDatasetUseCase = useResolve(CreateDatasetUseCase);
  const isLoading = ref(false);

  const create = async (dataset: any) => {
    isLoading.value = true; //
    const datasetId = await createDatasetUseCase.execute(dataset);
    isLoading.value = false;

    // TODO what happens if datasetId is null?
    // if(!datasetId)

    goToFeedbackTaskAnnotationPage(datasetId);
  };

  return {
    availableFieldTypes,
    availableQuestionTypes,
    create,
    isLoading,
  };
};
