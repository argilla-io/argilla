import { useResolve } from "ts-injecty";
import { ref, onBeforeMount } from "vue-demi";
import { useRecordMessages } from "./useRecordsMessages";
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
  const { getMessagesForLoading, getMessageForPagination } =
    useRecordMessages(recordCriteria);

  const recordsMessage = ref<string | null>(null);

  const getDatasetVectorsUseCase = useResolve(GetDatasetVectorsUseCase);
  const loadRecordsUseCase = useResolve(LoadRecordsToAnnotateUseCase);

  const datasetVectors = ref<DatasetVector[]>([]);
  const { state: records } = useRecords();

  const loadRecords = async (criteria: RecordCriteria) => {
    try {
      const newRecords = await loadRecordsUseCase.load(criteria);

      recordsMessage.value = getMessagesForLoading(newRecords);
    } catch (err) {
      criteria.reset();
    }
  };

  const paginateRecords = async (criteria: RecordCriteria) => {
    try {
      const isNextRecordExist = await loadRecordsUseCase.paginate(criteria);

      recordsMessage.value = getMessageForPagination(isNextRecordExist);
    } catch (err) {
      criteria.reset();
    }
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
    recordsMessage,
  };
};
