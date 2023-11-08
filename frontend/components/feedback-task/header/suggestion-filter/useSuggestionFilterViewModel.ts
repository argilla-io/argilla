import { ref } from "vue-demi";
import { Question } from "~/v1/domain/entities/question/Question";
import { SuggestionFilterList } from "~/v1/domain/entities/suggestion/SuggestionFilter";
import { useDebounce } from "~/v1/infrastructure/services";

export const useSuggestionFilterViewModel = ({
  datasetQuestions,
}: {
  datasetQuestions: Question[];
}) => {
  const debounce = useDebounce(500);
  const questionFilters = ref<SuggestionFilterList>(
    new SuggestionFilterList(datasetQuestions)
  );

  return { questionFilters, debounce };
};
