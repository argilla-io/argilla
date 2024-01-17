import { useResolve } from "ts-injecty";
import { ref, onBeforeMount } from "vue-demi";
import { LoadRecordsToAnnotateUseCase } from "@/v1/domain/usecases/load-records-to-annotate-use-case";
import { useRecords } from "@/v1/infrastructure/storage/RecordsStorage";
import { RecordCriteria } from "@/v1/domain/entities/record/RecordCriteria";
import { GetDatasetVectorsUseCase } from "@/v1/domain/usecases/get-dataset-vectors-use-case";
import { DatasetVector } from "~/v1/domain/entities/vector/DatasetVector";

export const useRecordFeedbackTaskViewModel = ({
  recordCriteria,
}: {
  recordCriteria: RecordCriteria;
}) => {
  const getDatasetVectorsUseCase = useResolve(GetDatasetVectorsUseCase);
  const getRecords = useResolve(LoadRecordsToAnnotateUseCase);

  const datasetVectors = ref<DatasetVector[]>([]);
  const { state: records } = useRecords();

  const loadRecords = async (criteria: RecordCriteria) => {
    try {
      await getRecords.load(criteria);
    } catch (err) {
      criteria.reset();
    }
  };

  const paginateRecords = async (criteria: RecordCriteria) => {
    let isNextRecordExist = false;

    try {
      isNextRecordExist = await getRecords.paginate(criteria);
    } catch (err) {
      criteria.reset();
    }

    return isNextRecordExist;
  };

  const loadVectors = async () => {
    datasetVectors.value = await getDatasetVectorsUseCase.execute(
      recordCriteria.datasetId
    );
  };

  onBeforeMount(() => {
    loadVectors();
  });

  return {
    records,
    datasetVectors,
    loadRecords,
    paginateRecords,
  };
};
