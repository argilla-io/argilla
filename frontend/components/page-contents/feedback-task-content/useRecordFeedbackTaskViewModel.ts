import { useResolve } from "ts-injecty";
import { GetRecordsForAnnotateUseCase } from "@/v1/domain/usecases/get-records-for-annotate-use-case";
import { useRecords } from "@/v1/infrastructure/storage/RecordsStorage";

export const useRecordFeedbackTaskViewModel = () => {
  const getRecords = useResolve(GetRecordsForAnnotateUseCase);
  const { state: records, clearRecords } = useRecords();

  const loadRecords = async (
    datasetId: string,
    offset: number,
    status: string,
    searchText: string
  ) => {
    return await getRecords.execute(datasetId, offset, status, searchText);
  };

  return { records, loadRecords, clearRecords };
};
