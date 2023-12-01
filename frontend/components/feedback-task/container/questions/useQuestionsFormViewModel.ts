import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Record } from "~/v1/domain/entities/record/Record";
import { ClearRecordUseCase } from "~/v1/domain/usecases/clear-record-use-case";
import { DiscardRecordUseCase } from "~/v1/domain/usecases/discard-record-use-case";
import { SubmitRecordUseCase } from "~/v1/domain/usecases/submit-record-use-case";
import { SaveDraftRecord } from "~/v1/domain/usecases/save-draft-use-case";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";
import { useQueue } from "~/v1/infrastructure/services/useQueue";
import { useBeforeUnload } from "~/v1/infrastructure/services/useBeforeUnload";

export const useQuestionFormViewModel = () => {
  const beforeUnload = useBeforeUnload();
  const queue = useQueue();
  const debounceForSubmit = useDebounce(300);
  const debounceForAutoSave = useDebounce(2000);
  const debounceForSavingMessage = useDebounce(1000);

  const draftSaving = ref(false);
  const isDiscarding = ref(false);
  const isSavingDraft = ref(false);
  const isSubmitting = ref(false);
  const discardUseCase = useResolve(DiscardRecordUseCase);
  const submitUseCase = useResolve(SubmitRecordUseCase);
  const clearUseCase = useResolve(ClearRecordUseCase);
  const saveDraftUseCase = useResolve(SaveDraftRecord);

  const discard = async (record: Record) => {
    isDiscarding.value = true;
    debounceForAutoSave.stop();
    beforeUnload.destroy();

    await queue.enqueue(() => {
      return discardUseCase.execute(record);
    });

    await debounceForSubmit.wait();

    isDiscarding.value = false;
  };

  const submit = async (record: Record) => {
    isSubmitting.value = true;
    debounceForAutoSave.stop();
    beforeUnload.destroy();

    await queue.enqueue(() => {
      return submitUseCase.execute(record);
    });

    await debounceForSubmit.wait();

    isSubmitting.value = false;
  };

  const saveDraftAllQueues = async (record: Record) => {
    isSavingDraft.value = true;
    debounceForAutoSave.stop();

    queue.enqueue(() => {
      return onSaveDraft(record);
    });
    await debounceForSubmit.wait();

    isSavingDraft.value = false;
  };

  const clear = (record: Record) => {
    debounceForAutoSave.stop();
    beforeUnload.destroy();

    queue.enqueue(() => {
      return clearUseCase.execute(record);
    });
  };

  const onSaveDraft = async (record: Record) => {
    if (!record.hasAnyQuestionAnswered) return;
    draftSaving.value = true;

    try {
      beforeUnload.confirm();
      await saveDraftUseCase.execute(record);
    } finally {
      await debounceForSavingMessage.wait();

      draftSaving.value = false;
      beforeUnload.destroy();
    }
  };

  const saveDraft = async (record: Record) => {
    if (record.isSubmitted) return;
    beforeUnload.confirm();
    await debounceForAutoSave.wait();

    queue.enqueue(() => {
      return onSaveDraft(record);
    });
  };

  const saveDraftImmediately = (record: Record) => {
    if (record.isSubmitted) return;
    debounceForAutoSave.stop();

    queue.enqueue(() => {
      return onSaveDraft(record);
    });
  };

  return {
    draftSaving,
    isDiscarding,
    isSubmitting,
    clear,
    submit,
    discard,
    saveDraft,
    saveDraftImmediately,
    saveDraftAllQueues,
  };
};
