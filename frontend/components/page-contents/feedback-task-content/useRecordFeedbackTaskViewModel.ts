import { isNil } from "lodash";
import { useResolve } from "ts-injecty";
import { RecordRepository } from "@/v1/infrastructure/RecordRepository";
import { useFeedback } from "~/v1/infrastructure/FeedbackStorage";

export const useRecordFeedbackTaskViewModel = () => {
  const recordRepository = useResolve(RecordRepository);
  const feedbackTask = useFeedback();

  const getRecordsFromBackend = async (
    datasetId: string,
    offset: number,
    status: string,
    searchText: string
  ) => {
    let records = [];
    let totalRecords = null;

    if (isNil(searchText) || !searchText.length) {
      ({ items: records } = await recordRepository.getRecords(
        datasetId,
        offset,
        status
      ));
    } else {
      ({ items: records, totalRecords } = await recordRepository.searchRecords(
        datasetId,
        offset,
        status,
        searchText
      ));
    }

    const feedback = feedbackTask.get();

    feedback.addRecords(records);

    feedbackTask.save(feedback);

    return { records, totalRecords };
  };

  return { getRecordsFromBackend };
};
