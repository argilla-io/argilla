import { ref, computed, watch } from "vue-demi";
import { useDraft } from "./useDraft";
import { useDiscard } from "./useDiscard";
import { useClear } from "./useClear";
import { useSubmit } from "./useSubmit";
import { useQuestionsFormFocus } from "./useQuestionsFormFocus";
import { useHandleGlobalKeys } from "./useHandleGlobalKeys";
import { Record } from "~/v1/domain/entities/record/Record";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";
import { useQueue } from "~/v1/infrastructure/services/useQueue";

export const useQuestionFormViewModel = (record: Record, context) => {
  record.initialize();

  // ACTIONS ON FORM
  const queue = useQueue();
  const debounceForAutoSave = useDebounce(2000);
  const debounceForSavingMessage = useDebounce(1000);
  const isFormTouched = ref(false);

  // computed
  const questionAreCompletedCorrectly = computed((): boolean => {
    return record.questionAreCompletedCorrectly();
  });

  const { onDiscard } = useDiscard(record, debounceForAutoSave, queue, context);
  const { onClear } = useClear(record, debounceForAutoSave, queue);
  const { isSubmitButtonDisabled, onSubmit } = useSubmit(
    record,
    questionAreCompletedCorrectly,
    isFormTouched,
    debounceForAutoSave,
    queue,
    context
  );
  const { draftSaving, onSaveDraftImmediately, saveDraft } = useDraft(
    record,
    debounceForAutoSave,
    debounceForSavingMessage,
    queue
  );

  // watch
  watch(
    record,
    () => {
      if (record.isModified) saveDraft(record);
      isFormTouched.value = record.isModified;
    },
    {
      immediate: true,
      deep: true,
    }
  );

  // FOR FOCUS AND GLOBAL KEYS
  const userComesFromOutside = ref(false);

  const {
    interactionCount,
    autofocusPosition,
    formHasFocus,
    onClickOutside,
    updateQuestionAutofocus,
    focusOnFirstQuestionFromOutside,
  } = useQuestionsFormFocus(record, userComesFromOutside);

  useHandleGlobalKeys(
    userComesFromOutside,
    focusOnFirstQuestionFromOutside,
    onSaveDraftImmediately,
    onSubmit,
    onClear,
    onDiscard
  );

  return {
    onClear,
    onSubmit,
    onDiscard,
    draftSaving,
    isSubmitButtonDisabled,
    isFormTouched,
    formHasFocus,
    interactionCount,
    onClickOutside,
    updateQuestionAutofocus,
    focusOnFirstQuestionFromOutside,
    autofocusPosition,
  };
};
