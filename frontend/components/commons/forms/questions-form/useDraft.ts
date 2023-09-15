import { ref } from "vue-demi";
import { useResolve } from "ts-injecty";
import { Record } from "~/v1/domain/entities/record/Record";
import { SaveDraftRecord } from "~/v1/domain/usecases/save-draft-use-case";
import { Debounce } from "~/v1/infrastructure/services/useDebounce";
import { Queue } from "~/v1/infrastructure/services/useQueue";
import { useBeforeUnload } from "~/v1/infrastructure/services/useBeforeUnload";

export const useDraft = (
  record: Record,
  debounceForAutoSave: Debounce,
  debounceForSavingMessage: Debounce,
  queue: Queue
) => {
  const beforeUnload = useBeforeUnload();
  const draftSaving = ref(false);
  const saveDraftUseCase = useResolve(SaveDraftRecord);

  const onSaveDraftImmediately = async () => {
    await saveDraftImmediately(record);
  };

  const saveDraftImmediately = (record: Record) => {
    if (record.isSubmitted) return;
    debounceForAutoSave.stop();

    queue.enqueue(() => {
      return onSaveDraft(record);
    });
  };

  const saveDraft = async (record: Record) => {
    if (record.isSubmitted) return;
    beforeUnload.confirm();
    await debounceForAutoSave.wait();

    queue.enqueue(() => {
      return onSaveDraft(record);
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
  return { draftSaving, onSaveDraftImmediately, saveDraft };
};
