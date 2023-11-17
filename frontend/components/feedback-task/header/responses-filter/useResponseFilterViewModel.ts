import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "vue-demi";
import { ResponseFilterList } from "~/v1/domain/entities/response/ResponseFilter";
import { GetDatasetQuestionsUseCase } from "~/v1/domain/usecases/get-dataset-questions-use-case";
import { useDebounce } from "~/v1/infrastructure/services";

export const useResponseFilterViewModel = ({
  datasetId,
}: {
  datasetId: string;
}) => {
  const debounce = useDebounce(500);
  const getQuestionsUseCase = useResolve(GetDatasetQuestionsUseCase);

  const isQuestionLoaded = ref(false);
  const questionFilters = ref<ResponseFilterList>();

  const loadQuestions = async () => {
    const questions = await getQuestionsUseCase.execute(datasetId);

    questionFilters.value = new ResponseFilterList(questions);

    isQuestionLoaded.value = true;
  };

  onBeforeMount(() => {
    loadQuestions();
  });

  return { isQuestionLoaded, questionFilters, debounce };
};
