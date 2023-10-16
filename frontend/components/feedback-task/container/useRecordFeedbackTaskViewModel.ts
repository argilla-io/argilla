import { useResolve } from "ts-injecty";
import {
  LoadRecordsMode,
  LoadRecordsToAnnotateUseCase,
} from "~/v1/domain/usecases/load-records-to-annotate-use-case";
import { useRecords } from "@/v1/infrastructure/storage/RecordsStorage";
import { GetUserMetricsUseCase } from "@/v1/domain/usecases/get-user-metrics-use-case";
import { RecordCriteria } from "~/v1/domain/entities/record/RecordCriteria";

export const useRecordFeedbackTaskViewModel = () => {
  const getRecords = useResolve(LoadRecordsToAnnotateUseCase);
  const getMetrics = useResolve(GetUserMetricsUseCase);
  const { state: records } = useRecords();

  const loadMetrics = (datasetId: string) => {
    getMetrics.execute(datasetId);
  };

  const loadRecords = async (
    mode: LoadRecordsMode,
    criteria: RecordCriteria
  ) => {
    await getRecords.load(mode, criteria);
  };

  const paginateRecords = (criteria: RecordCriteria) => {
    return getRecords.paginate(criteria);
  };

  return {
    records,
    loadMetrics,
    loadRecords,
    paginateRecords,
  };
};
