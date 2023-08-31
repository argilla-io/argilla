import { computed } from "vue-demi";
import { useGlobalShortcuts } from "./useGlobalShortcuts";
import { useDiscard } from "./useDiscard";
import { useClear } from "./useClear";
import { useSubmit } from "./useSubmit";
import { useDraft } from "./useDraft";
import { Record } from "~/v1/domain/entities/record/Record";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";
import { useQueue } from "~/v1/infrastructure/services/useQueue";

export const useQuestionFormViewModel = (record: Record, context) => {
  record.restore();

  const queue = useQueue();
  const debounce = useDebounce(2000);

  // computed
  const isFormTouched = computed((): boolean => {
    return record.isModified;
  });
  const questionAreCompletedCorrectly = computed((): boolean => {
    return record.questionAreCompletedCorrectly();
  });

  // actions on form
  const { onDiscard } = useDiscard(record, debounce, queue, context);
  const { onClear } = useClear(record, debounce, queue);
  const { isSubmitButtonDisabled, onSubmit } = useSubmit(
    record,
    questionAreCompletedCorrectly,
    isFormTouched,
    debounce,
    queue,
    context
  );
  const { draftSaving, onSaveDraftImmediately } = useDraft(
    record,
    debounce,
    queue
  );

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
