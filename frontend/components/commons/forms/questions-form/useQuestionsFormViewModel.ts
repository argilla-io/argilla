import { ref, computed, watch, SetupContext } from "vue-demi";
import { useDraft } from "./useDraft";
import { useDiscard } from "./useDiscard";
import { useClear } from "./useClear";
import { useSubmit } from "./useSubmit";
import { useQuestionsFormFocus } from "./useQuestionsFormFocus";
import { useHandleGlobalKeys } from "./useHandleGlobalKeys";
import { useQuestionFormState } from "./useQuestionFormState";
import { Record } from "~/v1/domain/entities/record/Record";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";
import { useQueue } from "~/v1/infrastructure/services/useQueue";
import { useBeforeUnload } from "~/v1/infrastructure/services/useBeforeUnload";

export const useQuestionFormViewModel = (
  record: Record,
  context: SetupContext<
    (
      | "on-discard-responses"
      | "on-submit-responses"
      | "on-question-form-touched"
    )[]
  >
) => {
  record.initialize();

  // QUESTIONS FORM STATE
  const { isFormTouched } = useQuestionFormState(record, context);

  // ACTIONS ON FORM
  const beforeUnload = useBeforeUnload();
  const queue = useQueue();
  const debounceForAutoSave = useDebounce(2000);
  const debounceForSavingMessage = useDebounce(1000);

  const questionAreCompletedCorrectly = computed((): boolean => {
    return record.questionAreCompletedCorrectly();
  });

  const { onDiscard } = useDiscard(
    record,
    beforeUnload,
    debounceForAutoSave,
    queue,
    context
  );
  const { onClear } = useClear(
    record,
    beforeUnload,
    debounceForAutoSave,
    queue
  );
  const { isSubmitButtonDisabled, onSubmit } = useSubmit(
    record,
    beforeUnload,
    questionAreCompletedCorrectly,
    isFormTouched,
    debounceForAutoSave,
    queue,
    context
  );
  const { draftSaving, onSaveDraftImmediately, saveDraft } = useDraft(
    record,
    beforeUnload,
    debounceForAutoSave,
    debounceForSavingMessage,
    queue
  );

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

  // FORM FOCUS AND GLOBAL KEYS
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
