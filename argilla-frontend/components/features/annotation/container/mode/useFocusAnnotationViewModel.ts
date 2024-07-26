import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Record } from "~/v1/domain/entities/record/Record";
import { DiscardRecordUseCase } from "~/v1/domain/usecases/discard-record-use-case";
import { SubmitRecordUseCase } from "~/v1/domain/usecases/submit-record-use-case";
import { SaveDraftUseCase } from "~/v1/domain/usecases/save-draft-use-case";

export const useFocusAnnotationViewModel = () => {
  const isDraftSaving = ref(false);
  const isDiscarding = ref(false);
  const isSubmitting = ref(false);
  const discardUseCase = useResolve(DiscardRecordUseCase);
  const submitUseCase = useResolve(SubmitRecordUseCase);
  const saveDraftUseCase = useResolve(SaveDraftUseCase);

  const discard = async (record: Record) => {
    try {
      isDiscarding.value = true;

      await discardUseCase.execute(record);
    } catch {
    } finally {
      isDiscarding.value = false;
    }
  };

  const submit = async (record: Record) => {
    try {
      isSubmitting.value = true;

      await submitUseCase.execute(record);
    } catch {
    } finally {
      isSubmitting.value = false;
    }
  };

  const saveAsDraft = async (record: Record) => {
    try {
      isDraftSaving.value = true;

      await saveDraftUseCase.execute(record);
    } catch {
    } finally {
      isDraftSaving.value = false;
    }
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
