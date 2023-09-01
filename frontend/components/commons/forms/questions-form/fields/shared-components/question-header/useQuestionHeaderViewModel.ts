import { ref, Ref, computed, watch } from "vue-demi";
import { Question } from "~/v1/domain/entities/question/Question";

export const useQuestionHeaderViewModel = (question: Question) => {
  const matchSuggestion = ref<boolean>(question.matchSuggestion);
  const tooltipMessage = ref<string>(question.description);
  const openTooltip = ref<boolean>(false);
  const timer = ref<NodeJS.Timeout>(null);

  const showIcon: Ref<boolean> = computed(() => {
    return !!question.description?.length;
  });

  watch(
    () => question.matchSuggestion,
    () => {
      matchSuggestion.value = question.matchSuggestion;
    }
  );
  watch(
    () => question.description,
    () => {
      if (timer.value) clearTimeout(timer.value);
      openTooltip.value = true;
      tooltipMessage.value = question.description;

      timer.value = setTimeout(() => {
        openTooltip.value = false;
      }, 2000);
    }
  );

  return { matchSuggestion, showIcon, tooltipMessage, openTooltip };
};
