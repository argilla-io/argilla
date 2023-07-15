import { useResolve } from "ts-injecty";
import { GetRecordsForAnnotateUseCase } from "@/v1/domain/usecases/get-records-for-annotate-use-case";
import { useRecords } from "@/v1/infrastructure/storage/RecordsStorage";
import { GetUserMetricsUseCase } from "~/v1/domain/usecases/get-user-metrics-use-case";

export const useRecordFeedbackTaskViewModel = () => {
  const getRecords = useResolve(GetRecordsForAnnotateUseCase);
  const getMetrics = useResolve(GetUserMetricsUseCase);
  const { state: records, clearRecords } = useRecords();

  const loadMetrics = (datasetId: string) => {
    getMetrics.execute(datasetId);
  };

  const loadRecords = async (
    datasetId: string,
    page: number,
    status: string,
    searchText: string
  ) => {
    return await getRecords.execute(datasetId, page, status, searchText);
  };

  return { records, loadMetrics, loadRecords, clearRecords };
};
