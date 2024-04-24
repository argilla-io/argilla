import { useRecords } from "~/v1/infrastructure/storage/RecordsStorage";

export const usePaginationFeedbackTaskViewModel = () => {
  const { state: records } = useRecords();

  return { records };
};
