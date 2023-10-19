import { useResolve } from "ts-injecty";
import {
  LoadRecordsMode,
  LoadRecordsToAnnotateUseCase,
} from "~/v1/domain/usecases/load-records-to-annotate-use-case";
import { useRecords } from "@/v1/infrastructure/storage/RecordsStorage";
import { RecordCriteria } from "~/v1/domain/entities/record/RecordCriteria";

export const useRecordFeedbackTaskViewModel = () => {
  const getRecords = useResolve(LoadRecordsToAnnotateUseCase);
  const { state: records } = useRecords();

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
    loadRecords,
    paginateRecords,
  };
};
