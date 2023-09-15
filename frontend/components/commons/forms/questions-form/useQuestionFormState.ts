import { ref, onUnmounted, watch } from "vue-demi";
import { questionsFormState } from "./questionsFormState.store";
import { Record } from "~/v1/domain/entities/record/Record";

export const useQuestionFormState = (record: Record, { emit }) => {
  const isFormTouched = ref(false);

  watch(isFormTouched, (isFormTouched) => {
    if (record.isSubmitted) emitIsQuestionsFormTouched(isFormTouched);
  });

  const emitIsQuestionsFormTouched = (isFormTouched: boolean) => {
    emit("on-question-form-touched", isFormTouched);

    questionsFormState.value.setIsQuestionsFormTouched(isFormTouched);
  };

  onUnmounted(() => {
    emitIsQuestionsFormTouched(false);
  });

  return { isFormTouched };
};
