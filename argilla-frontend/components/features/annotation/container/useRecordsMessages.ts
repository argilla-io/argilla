import { RecordCriteria } from "~/v1/domain/entities/record/RecordCriteria";
import { Records } from "~/v1/domain/entities/record/Records";
import { useMetrics } from "~/v1/infrastructure/storage/MetricsStorage";
import { useTeamProgress } from "~/v1/infrastructure/storage/TeamProgressStorage";

export const useRecordMessages = (recordCriteria: RecordCriteria) => {
  const { state: metrics } = useMetrics();
  const { state: progress } = useTeamProgress();

  const getMessagesForLoading = (records: Records) => {
    if (metrics.isEmpty) {
      return "The dataset is empty, start to upload records (include code snippet for admin/owner) / come back soon (annotator)";
    }

    if (progress.isCompleted) {
      return "🎉 The task is completed!";
    }

    if (!records.hasRecordsToAnnotate) {
      const { status } = recordCriteria.committed;

      if (recordCriteria.isFilteredByText) {
        return `You have no ${status} records matching your query`;
      }

      if (status === "draft") {
        return "You have no records with draft responses / You have no records in draft";
      }

      if (status === "submitted") {
        return "You have not submitted any record yet";
      }

      return `You have no ${status} records`;
    }

    return null;
  };

  const getMessageForPagination = (isNextRecordExist: boolean) => {
    if (progress.isCompleted) {
      return "🎉 The task is completed!";
    }

    if (!isNextRecordExist) {
      const { status } = recordCriteria.committed;

      if (status === "pending") {
        return "🎉 Your have no pending records to annotate";
      }

      if (status === "draft") {
        return "Your have no draft records to review";
      }

      if (status === "discarded") {
        return `You have no ${status} records`;
      }
    }

    return null;
  };

  return {
    getMessagesForLoading,
    getMessageForPagination,
  };
};
