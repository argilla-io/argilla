import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "vue-demi";
import {
  DatasetVector,
  GetDatasetVectorsUseCase,
} from "~/v1/domain/usecases/get-dataset-vectors-use-case";

export const useRecordFieldsViewModel = () => {
  const datasetVectors = ref<DatasetVector[]>([]);
  const getDatasetVectorsUseCase = useResolve(GetDatasetVectorsUseCase);
  const loadVectors = async () => {
    datasetVectors.value = await getDatasetVectorsUseCase.execute("");
  };
  onBeforeMount(() => {
    loadVectors();
  });
  return { datasetVectors };
};
