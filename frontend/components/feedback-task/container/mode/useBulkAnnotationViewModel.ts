import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Notification } from "~/models/Notifications";
import { Record } from "~/v1/domain/entities/record/Record";
import { DiscardBulkAnnotationUseCase } from "~/v1/domain/usecases/discard-bulk-annotation-use-case";
import { SaveDraftBulkAnnotationUseCase } from "~/v1/domain/usecases/save-draft-bulk-annotation-use-case";
import { SubmitBulkAnnotationUseCase } from "~/v1/domain/usecases/submit-bulk-annotation-use-case";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";
import { useTranslate } from "~/v1/infrastructure/services/useTranslate";

export const useBulkAnnotationViewModel = () => {
  const debounceForSubmit = useDebounce(300);

  const isDraftSaving = ref(false);
  const isDiscarding = ref(false);
  const isSubmitting = ref(false);
  const discardUseCase = useResolve(DiscardBulkAnnotationUseCase);
  const submitUseCase = useResolve(SubmitBulkAnnotationUseCase);
  const saveDraftUseCase = useResolve(SaveDraftBulkAnnotationUseCase);
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

  const saveAsDraft = async (records: Record[], recordReference: Record) => {
    try {
      isDraftSaving.value = true;

      const allSuccessful = await saveDraftUseCase.execute(
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
    }

    return false;
  };

  return {
    isDraftSaving,
    isDiscarding,
    isSubmitting,
    submit,
    discard,
    saveAsDraft,
  };
};
