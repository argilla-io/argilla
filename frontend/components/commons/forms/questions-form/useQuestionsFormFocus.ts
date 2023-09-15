import { Ref, computed, ref } from "vue-demi";
import { Record } from "~/v1/domain/entities/record/Record";

export const useQuestionsFormFocus = (
  record: Record,
  userComesFromOutside: Ref<boolean>
) => {
  const interactionCount = ref(0);
  const autofocusPosition = ref(0);

  const formHasFocus = computed(() => {
    return autofocusPosition.value || autofocusPosition.value === 0;
  });

  const numberOfQuestions = computed(() => {
    return record.questions.length;
  });

  const onClickOutside = () => {
    autofocusPosition.value = null;
    userComesFromOutside.value = true;
  };

  const updateQuestionAutofocus = (index: number) => {
    interactionCount.value++;
    autofocusPosition.value = Math.min(
      numberOfQuestions.value - 1,
      Math.max(0, index)
    );
  };

  const focusOnFirstQuestion = (event: Event) => {
    event.preventDefault();
    updateQuestionAutofocus(0);
  };

  const focusOnFirstQuestionFromOutside = (event) => {
    if (!userComesFromOutside.value) return;
    if (event.srcElement.id || event.srcElement.getAttribute("for")) return;

    userComesFromOutside.value = false;
    focusOnFirstQuestion(event);
  };

  return {
    interactionCount,
    autofocusPosition,
    formHasFocus,
    onClickOutside,
    updateQuestionAutofocus,
    focusOnFirstQuestionFromOutside,
  };
};
