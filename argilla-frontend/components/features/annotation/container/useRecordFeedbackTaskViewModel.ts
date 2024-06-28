import { useResolve } from "ts-injecty";
import { LoadRecordsToAnnotateUseCase } from "@/v1/domain/usecases/load-records-to-annotate-use-case";
import { useRecords } from "@/v1/infrastructure/storage/RecordsStorage";
import { RecordCriteria } from "@/v1/domain/entities/record/RecordCriteria";
import { GetDatasetVectorsUseCase } from "@/v1/domain/usecases/get-dataset-vectors-use-case";

export const useRecordFeedbackTaskViewModel = ({
  recordCriteria,
}: {
  recordCriteria: RecordCriteria;
}) => {
  const getDatasetVectorsUseCase = useResolve(GetDatasetVectorsUseCase);
  const loadRecordsUseCase = useResolve(LoadRecordsToAnnotateUseCase);
  const { state: records } = useRecords();

  const loadRecords = async (criteria: RecordCriteria) => {
    try {
      await loadRecordsUseCase.load(criteria);
    } catch (err) {
      criteria.reset();
    }
  };

  const paginateRecords = async (criteria: RecordCriteria) => {
    let isNextRecordExist = false;

    try {
      isNextRecordExist = await loadRecordsUseCase.paginate(criteria);
    } catch (err) {
      criteria.reset();
    }

    return isNextRecordExist;
  };

  const { data: datasetVectors } = useLazyAsyncData(
    recordCriteria.datasetId,
    () => getDatasetVectorsUseCase.execute(recordCriteria.datasetId)
  );

  return {
    records,
    datasetVectors,
    loadRecords,
    paginateRecords,
  };
};
