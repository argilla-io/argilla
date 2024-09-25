import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Record } from "~/v1/domain/entities/record/Record";
import { RecordCriteria } from "~/v1/domain/entities/record/RecordCriteria";
import { Records } from "~/v1/domain/entities/record/Records";
import {
  AvailableStatus,
  BulkAnnotationUseCase,
} from "~/v1/domain/usecases/bulk-annotation-use-case";
import { useNotifications } from "~/v1/infrastructure/services/useNotifications";
import { useTranslate } from "~/v1/infrastructure/services/useTranslate";

export const useBulkAnnotationViewModel = ({
  records,
}: {
  records: Records;
}) => {
  const notification = useNotifications();

  const affectAllRecords = ref(false);
  const progress = ref(0);

  const isDraftSaving = ref(false);
  const isDiscarding = ref(false);
  const isSubmitting = ref(false);
  const bulkAnnotationUseCase = useResolve(BulkAnnotationUseCase);

  const { t } = useTranslate();

  const checkIfSomeFilterIsActive = (criteria: RecordCriteria) => {
    return (
      criteria.isFilteredByText ||
      criteria.isFilteredByResponse ||
      criteria.isFilteredByMetadata ||
      criteria.isFilteredBySuggestion
    );
  };

  const annotateBulk = async (
    status: AvailableStatus,
    criteria: RecordCriteria,
    recordReference: Record,
    selectedRecords: Record[]
  ) => {
    let allSuccessful = false;
    try {
      const totalRecords = records.total;
      const isAffectingAllRecords = affectAllRecords.value;

      allSuccessful = await bulkAnnotationUseCase.execute(
        status,
        criteria,
        recordReference,
        selectedRecords,
        isAffectingAllRecords,
        (value) => {
          progress.value = value;
        }
      );

      if (!allSuccessful) {
        notification.notify({
          message: t("some_records_failed_to_annotate"),
          type: "danger",
        });
      } else if (isAffectingAllRecords) {
        notification.notify({
          message: t("bulkAnnotation.allRecordsAnnotated", {
            total: totalRecords,
            action: t(`bulkAnnotation.affectedAll.${status}`).toLowerCase(),
          }),
          type: "info",
        });
      }
    } catch {
    } finally {
      affectAllRecords.value = false;
      progress.value = 0;
    }

    return allSuccessful;
  };

  const discard = async (
    criteria: RecordCriteria,
    recordReference: Record,
    records: Record[]
  ) => {
    isDiscarding.value = true;

    const allSuccessful = await annotateBulk(
      "discarded",
      criteria,
      recordReference,
      records
    );

    isDiscarding.value = false;

    return allSuccessful;
  };

  const submit = async (
    criteria: RecordCriteria,
    recordReference: Record,
    records: Record[]
  ) => {
    isSubmitting.value = true;

    const allSuccessful = await annotateBulk(
      "submitted",
      criteria,
      recordReference,
      records
    );

    isSubmitting.value = false;

    return allSuccessful;
  };

  const saveAsDraft = async (
    criteria: RecordCriteria,
    recordReference: Record,
    records: Record[]
  ) => {
    isDraftSaving.value = true;

    const allSuccessful = await annotateBulk(
      "draft",
      criteria,
      recordReference,
      records
    );

    isDraftSaving.value = false;

    return allSuccessful;
  };

  return {
    affectAllRecords,
    progress,
    isDraftSaving,
    isDiscarding,
    isSubmitting,
    submit,
    discard,
    saveAsDraft,
    checkIfSomeFilterIsActive,
  };
};
