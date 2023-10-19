import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "vue-demi";
import {
  DatasetVector,
  GetDatasetVectorsUseCase,
} from "~/v1/domain/usecases/get-dataset-vectors-use-case";

export const useRecordFieldsAndSimilarityViewModel = () => {
  const datasetVectors = ref<DatasetVector[]>([]);
  const getDatasetVectorsUseCase = useResolve(GetDatasetVectorsUseCase);
  const loadVectors = async () => {
    try {
      datasetVectors.value = await getDatasetVectorsUseCase.execute("");
    } catch (error) {
      // TODO !
    }
  };

  onBeforeMount(() => {
    loadVectors();
  });

  return { datasetVectors };
};
