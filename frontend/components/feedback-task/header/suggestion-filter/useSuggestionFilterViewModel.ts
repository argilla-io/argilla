import { ref } from "vue-demi";
import { Question } from "~/v1/domain/entities/question/Question";
import { QuestionFilterList } from "~/v1/domain/entities/question/QuestionFilter";
import { useDebounce } from "~/v1/infrastructure/services";

export const useSuggestionFilterViewModel = ({
  datasetQuestions,
}: {
  datasetQuestions: Question[];
}) => {
  const debounce = useDebounce(500);
  const questionFilters = ref<QuestionFilterList>(
    new QuestionFilterList(datasetQuestions)
  );

  return { questionFilters, debounce };
};
