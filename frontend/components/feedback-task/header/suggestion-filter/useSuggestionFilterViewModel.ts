import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "vue-demi";
import { SuggestionFilterList } from "~/v1/domain/entities/suggestion/SuggestionFilter";
import { GetDatasetQuestionsUseCase } from "~/v1/domain/usecases/get-dataset-questions-use-case";
import { GetDatasetSuggestionsAgentsUseCase } from "~/v1/domain/usecases/get-dataset-suggestions-agents-use-case";
import { useDebounce } from "~/v1/infrastructure/services";

export const useSuggestionFilterViewModel = ({
  datasetId,
}: {
  datasetId: string;
}) => {
  const debounce = useDebounce(500);
  const isSuggestionFiltersLoaded = ref(false);
  const getQuestionsUseCase = useResolve(GetDatasetQuestionsUseCase);
  const getAgentsUseCase = useResolve(GetDatasetSuggestionsAgentsUseCase);

  const suggestionFilters = ref<SuggestionFilterList>();

  const loadFilterInformation = async () => {
    const questions = await getQuestionsUseCase.execute(datasetId);

    suggestionFilters.value = new SuggestionFilterList(questions);

    getAgentsUseCase.execute(datasetId).then((agents) => {
      suggestionFilters.value.addAgents(agents);
    });

    isSuggestionFiltersLoaded.value = true;
  };

  onBeforeMount(() => {
    loadFilterInformation();
  });

  return { isSuggestionFiltersLoaded, suggestionFilters, debounce };
};
