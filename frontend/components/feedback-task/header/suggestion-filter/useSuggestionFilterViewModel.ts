import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "vue-demi";
import { Question } from "~/v1/domain/entities/question/Question";
import { SuggestionFilterList } from "~/v1/domain/entities/suggestion/SuggestionFilter";
import { GetDatasetSuggestionsAgentsUseCase } from "~/v1/domain/usecases/get-dataset-suggestions-agents-use-case";
import { useDebounce } from "~/v1/infrastructure/services";

export const useSuggestionFilterViewModel = ({
  datasetQuestions,
  datasetId,
}: {
  datasetQuestions: Question[];
  datasetId: string;
}) => {
  const debounce = useDebounce(500);
  const getAgentsUseCase = useResolve(GetDatasetSuggestionsAgentsUseCase);

  const suggestionFilters = ref<SuggestionFilterList>(
    new SuggestionFilterList(datasetQuestions)
  );

  const loadFilterInformation = () => {
    getAgentsUseCase.execute(datasetId).then((agents) => {
      suggestionFilters.value.addAgents(agents);
    });
  };

  onBeforeMount(() => {
    loadFilterInformation();
  });

  return { suggestionFilters, debounce };
};
