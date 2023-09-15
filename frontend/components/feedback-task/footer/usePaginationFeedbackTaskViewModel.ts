import { computed } from "vue-demi";
import { useRecords } from "~/v1/infrastructure/storage/RecordsStorage";
import { questionsFormState } from "~/components/commons/forms/questions-form/questionsFormState.store";

export const usePaginationFeedbackTaskViewModel = () => {
  const { state: records } = useRecords();

  // QUESTIONS FORM STATE
  const isQuestionsFormTouched = computed(
    () => questionsFormState.value.isQuestionsFormTouched
  );

  return { records, isQuestionsFormTouched };
};
