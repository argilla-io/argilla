import { useResolve } from "ts-injecty";
import {
  LoadRecordsMode,
  LoadRecordsToAnnotateUseCase,
} from "~/v1/domain/usecases/load-records-to-annotate-use-case";
import { useRecords } from "@/v1/infrastructure/storage/RecordsStorage";
import { GetUserMetricsUseCase } from "@/v1/domain/usecases/get-user-metrics-use-case";
import { useRoutes } from "~/v1/infrastructure/services";

export const useRecordFeedbackTaskViewModel = () => {
  const routes = useRoutes();
  const getRecords = useResolve(LoadRecordsToAnnotateUseCase);
  const getMetrics = useResolve(GetUserMetricsUseCase);
  const { state: records } = useRecords();

  const loadMetrics = (datasetId: string) => {
    getMetrics.execute(datasetId);
  };

  const loadRecords = async (
    mode: LoadRecordsMode,
    datasetId: string,
    page: number,
    status: string,
    searchText: string,
    metadataFilter: string[],
    sortBy: string[]
  ) => {
    await getRecords.execute(
      mode,
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
    routes,
  };
};
