import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Notification } from "~/models/Notifications";
import { Record } from "~/v1/domain/entities/record/Record";
import { RecordCriteria } from "~/v1/domain/entities/record/RecordCriteria";
import { DiscardBulkAnnotationUseCase } from "~/v1/domain/usecases/discard-bulk-annotation-use-case";
import { SaveDraftBulkByCriteriaUseCase } from "~/v1/domain/usecases/save-draft-bulk-annotation-by-criteria-use-case";
import { SaveDraftBulkAnnotationUseCase } from "~/v1/domain/usecases/save-draft-bulk-annotation-use-case";
import { SubmitBulkAnnotationUseCase } from "~/v1/domain/usecases/submit-bulk-annotation-use-case";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";
import { useTranslate } from "~/v1/infrastructure/services/useTranslate";

export const useBulkAnnotationViewModel = () => {
  const debounceForSubmit = useDebounce(300);

  const affectAllRecords = ref(false);
  const progress = ref(0);
  const isDraftSaving = ref(false);
  const isDiscarding = ref(false);
  const isSubmitting = ref(false);
  const discardUseCase = useResolve(DiscardBulkAnnotationUseCase);
  const submitUseCase = useResolve(SubmitBulkAnnotationUseCase);
  const saveDraftUseCase = useResolve(SaveDraftBulkAnnotationUseCase);

  const saveDraftByCriteriaUseCase = useResolve(SaveDraftBulkByCriteriaUseCase);

  const t = useTranslate();

  const discard = async (records: Record[], recordReference: Record) => {
    try {
      isDiscarding.value = true;

      const allSuccessful = await discardUseCase.execute(
        records,
        recordReference
      );

      if (!allSuccessful) {
        Notification.dispatch("notify", {
          message: t("some_records_failed_to_annotate"),
          type: "error",
        });
      }

      await debounceForSubmit.wait();

      return allSuccessful;
    } catch (error) {
    } finally {
      isDiscarding.value = false;
    }

    return false;
  };

  const submit = async (records: Record[], recordReference: Record) => {
    try {
      isSubmitting.value = true;

      const allSuccessful = await submitUseCase.execute(
        records,
        recordReference
      );

      if (!allSuccessful) {
        Notification.dispatch("notify", {
          message: t("some_records_failed_to_annotate"),
          type: "error",
        });
      }

      await debounceForSubmit.wait();

      return allSuccessful;
    } catch (error) {
    } finally {
      isSubmitting.value = false;
    }

    return false;
  };

  const saveAsDraft = async (
    criteria: RecordCriteria,
    records: Record[],
    recordReference: Record
  ) => {
    try {
      isDraftSaving.value = true;

      let allSuccessful = false;

      if (affectAllRecords.value)
        allSuccessful = await saveDraftByCriteriaUseCase.execute(
          criteria,
          recordReference,
          (value) => (progress.value = value * 100)
        );
      else
        allSuccessful = await saveDraftUseCase.execute(
          records,
          recordReference
        );

      if (!allSuccessful) {
        Notification.dispatch("notify", {
          message: t("some_records_failed_to_annotate"),
          type: "error",
        });
      }

      await debounceForSubmit.wait();

      return allSuccessful;
    } catch (error) {
    } finally {
      isDraftSaving.value = false;
      affectAllRecords.value = false;
      progress.value = 0;
    }

    return false;
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
  };
};
