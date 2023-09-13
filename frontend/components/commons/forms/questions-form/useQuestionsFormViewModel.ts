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
  const debounce = useDebounce(2000);

  const draftSaving = ref(false);
  const discardUseCase = useResolve(DiscardRecordUseCase);
  const submitUseCase = useResolve(SubmitRecordUseCase);
  const clearUseCase = useResolve(ClearRecordUseCase);
  const saveDraftUseCase = useResolve(SaveDraftRecord);

  const discard = (record: Record) => {
    debounce.stop();

    queue.enqueue(() => {
      return discardUseCase.execute(record);
    });
  };

  const submit = (record: Record) => {
    debounce.stop();

    queue.enqueue(() => {
      return submitUseCase.execute(record);
    });
  };

  const clear = (record: Record) => {
    debounce.stop();

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
      draftSaving.value = false;
      beforeUnload.destroy();
    }
  };

  const saveDraft = async (record: Record) => {
    if (record.isSubmitted) return;
    beforeUnload.confirm();
    await debounce.wait();

    queue.enqueue(() => {
      return onSaveDraft(record);
    });
  };

  const saveDraftImmediately = (record: Record) => {
    if (record.isSubmitted) return;
    debounce.stop();

    queue.enqueue(() => {
      return onSaveDraft(record);
    });
  };

  return {
    clear,
    submit,
    discard,
    saveDraft,
    draftSaving,
    saveDraftImmediately,
  };
};
