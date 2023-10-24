import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "vue-demi";
import { RecordCriteria } from "@/v1/domain/entities/record/RecordCriteria";
import {
  DatasetVector,
  GetDatasetVectorsUseCase,
} from "~/v1/domain/usecases/get-dataset-vectors-use-case";

export const useRecordFieldsAndSimilarityViewModel = ({
  recordCriteria,
}: {
  recordCriteria: RecordCriteria;
}) => {
  const datasetVectors = ref<DatasetVector[]>([]);
  const getDatasetVectorsUseCase = useResolve(GetDatasetVectorsUseCase);

  const loadVectors = async () => {
    try {
      datasetVectors.value = await getDatasetVectorsUseCase.execute(
        recordCriteria.datasetId
      );
    } catch (error) {
      // TODO !
    }
  };

  onBeforeMount(() => {
    loadVectors();
  });

  return { datasetVectors };
};
