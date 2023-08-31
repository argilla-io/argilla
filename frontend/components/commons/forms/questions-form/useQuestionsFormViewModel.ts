import { useResolve } from "ts-injecty";
import { ref, computed, watch } from "vue-demi";
import { useGlobalShortcuts } from "./useGlobalShortcuts";
import { Record } from "~/v1/domain/entities/record/Record";
import { ClearRecordUseCase } from "~/v1/domain/usecases/clear-record-use-case";
import { DiscardRecordUseCase } from "~/v1/domain/usecases/discard-record-use-case";
import { SubmitRecordUseCase } from "~/v1/domain/usecases/submit-record-use-case";
import { SaveDraftRecord } from "~/v1/domain/usecases/save-draft-use-case";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";
import { useQueue } from "~/v1/infrastructure/services/useQueue";

export const useQuestionFormViewModel = (record: Record, { emit }) => {
  record.restore();

  const queue = useQueue();
  const debounce = useDebounce(2000);

  const draftSaving = ref(false);
  const discardUseCase = useResolve(DiscardRecordUseCase);
  const submitUseCase = useResolve(SubmitRecordUseCase);
  const clearUseCase = useResolve(ClearRecordUseCase);
  const saveDraftUseCase = useResolve(SaveDraftRecord);

  // computed
  const isFormTouched = computed((): boolean => {
    return record.isModified;
  });
  const questionAreCompletedCorrectly = computed((): boolean => {
    return record.questionAreCompletedCorrectly();
  });
  const isSubmitButtonDisabled = computed((): boolean => {
    if (record.isSubmitted)
      return !isFormTouched.value || !questionAreCompletedCorrectly.value;

    return !questionAreCompletedCorrectly.value;
  });

  // watch
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

  // action on questions
  const onSubmit = async () => {
    if (!questionAreCompletedCorrectly) return;

    await submit(record);

    emit("on-submit-responses");
  };

  const onDiscard = async () => {
    await discard(record);

    emit("on-discard-responses");
  };

  const onClear = async () => {
    await clear(record);
  };

  // private methods
  const submit = (record: Record) => {
    debounce.stop();

    queue.enqueue(() => {
      return submitUseCase.execute(record);
    });
  };

  const discard = (record: Record) => {
    debounce.stop();

    queue.enqueue(() => {
      return discardUseCase.execute(record);
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
      await saveDraftUseCase.execute(record);
    } finally {
      draftSaving.value = false;
    }
  };

  const saveDraft = async (record: Record) => {
    if (record.isSubmitted) return;
    await debounce.wait();

    queue.enqueue(() => {
      return onSaveDraft(record);
    });
  };

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

  // shortcuts
  useGlobalShortcuts(onSaveDraftImmediately, onSubmit, onClear, onDiscard);

  return {
    onClear,
    onSubmit,
    onDiscard,
    draftSaving,
    isFormTouched,
    isSubmitButtonDisabled,
  };
};
