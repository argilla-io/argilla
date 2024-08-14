import { RecordCriteria } from "~/v1/domain/entities/record/RecordCriteria";
import { Records } from "~/v1/domain/entities/record/Records";
import { useRole, useTranslate } from "~/v1/infrastructure/services";
import { useMetrics } from "~/v1/infrastructure/storage/MetricsStorage";
import { useTeamProgress } from "~/v1/infrastructure/storage/TeamProgressStorage";

export const useRecordMessages = (recordCriteria: RecordCriteria) => {
  const t = useTranslate();
  const { isAdminOrOwnerRole } = useRole();
  const { state: metrics } = useMetrics();
  const { state: progress } = useTeamProgress();

  const getMessagesForLoading = (records: Records) => {
    if (metrics.isEmpty) {
      return isAdminOrOwnerRole.value
        ? t("noRecordsMessages.datasetEmptyForAdmin")
        : t("noRecordsMessages.datasetEmptyForAnnotator");
    }

    if (progress.isCompleted) {
      return t("noRecordsMessages.taskDistributionCompleted");
    }

    if (!records.hasRecordsToAnnotate) {
      const { status } = recordCriteria.committed;

      if (recordCriteria.isFilteredByText) {
        return t("noRecordsMessages.noRecordsFound", status);
      }

      if (status === "draft") {
        return t("noRecordsMessages.noDraftRecords");
      }

      if (status === "submitted") {
        return t("noRecordsMessages.noSubmittedRecords");
      }

      return t("noRecordsMessages.noRecords", status);
    }

    return null;
  };

  const getMessageForPagination = (isNextRecordExist: boolean) => {
    if (progress.isCompleted) {
      return t("noRecordsMessages.taskDistributionCompleted");
    }

    if (!isNextRecordExist) {
      const { status } = recordCriteria.committed;

      if (status === "pending") {
        return t("noRecordsMessages.noPendingRecordsToAnnotate");
      }

      if (status === "draft") {
        return t("noRecordsMessages.noDraftRecordsToReview");
      }

      if (status === "discarded") {
        return t("noRecordsMessages.noRecords", status);
      }
    }

    return null;
  };

  return {
    getMessagesForLoading,
    getMessageForPagination,
  };
};
