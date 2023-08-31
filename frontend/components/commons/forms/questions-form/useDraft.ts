import { ref, watch } from "vue-demi";
import { useResolve } from "ts-injecty";
import { Record } from "~/v1/domain/entities/record/Record";
import { SaveDraftRecord } from "~/v1/domain/usecases/save-draft-use-case";
import { Debounce } from "~/v1/infrastructure/services/useDebounce";
import { Queue } from "~/v1/infrastructure/services/useQueue";

export const useDraft = (record: Record, debounce: Debounce, queue: Queue) => {
  const draftSaving = ref(false);
  const saveDraftUseCase = useResolve(SaveDraftRecord);

  watch(
    record,
    () => {
      if (record.isModified) saveDraft(record);
    },
    {
      immediate: true,
      deep: true,
    }
  );

  const onSaveDraftImmediately = async () => {
    await saveDraftImmediately(record);
  };

  const saveDraftImmediately = (record: Record) => {
    if (record.isSubmitted) return;
    debounce.stop();

    queue.enqueue(() => {
      return onSaveDraft(record);
    });
  };

  const saveDraft = async (record: Record) => {
    if (record.isSubmitted) return;
    await debounce.wait();

    queue.enqueue(() => {
      return onSaveDraft(record);
    });
  };

  const onSaveDraft = async (record: Record) => {
    if (!record.hasAnyQuestionAnswered) return;
    draftSaving.value = true;

    try {
      await saveDraftUseCase.execute(record);
    } finally {
      draftSaving.value = false;
    }
  };

  return { draftSaving, onSaveDraftImmediately };
};
