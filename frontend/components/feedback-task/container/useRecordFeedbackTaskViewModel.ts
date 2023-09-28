import { useResolve } from "ts-injecty";
import { GetRecordsToAnnotateUseCase } from "@/v1/domain/usecases/get-records-to-annotate-use-case";
import { useRecords } from "@/v1/infrastructure/storage/RecordsStorage";
import { GetUserMetricsUseCase } from "@/v1/domain/usecases/get-user-metrics-use-case";
import { useRoutes } from "~/v1/infrastructure/services";

export const useRecordFeedbackTaskViewModel = () => {
  const routes = useRoutes();
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
    searchText: string,
    metadataFilter: string[],
    sortBy: string[]
  ) => {
    await getRecords.execute(
      datasetId,
      page,
      status,
      searchText,
      metadataFilter,
      sortBy
    );
  };

  return {
    records,
    loadMetrics,
    loadRecords,
    clearRecords,
    routes,
  };
};
