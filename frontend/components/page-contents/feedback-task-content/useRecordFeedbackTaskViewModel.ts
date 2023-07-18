import { useResolve } from "ts-injecty";
import { GetRecordsToAnnotateUseCase } from "@/v1/domain/usecases/get-records-to-annotate-use-case";
import { useRecords } from "@/v1/infrastructure/storage/RecordsStorage";
import { GetUserMetricsUseCase } from "@/v1/domain/usecases/get-user-metrics-use-case";

export const useRecordFeedbackTaskViewModel = () => {
  const getRecords = useResolve(GetRecordsToAnnotateUseCase);
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
    await getRecords.execute(datasetId, page, status, searchText);
  };

  return { records, loadMetrics, loadRecords, clearRecords };
};
