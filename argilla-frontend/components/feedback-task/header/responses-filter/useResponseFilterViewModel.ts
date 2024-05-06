import { ref } from "vue-demi";
import { Question } from "~/v1/domain/entities/question/Question";
import { ResponseFilterList } from "~/v1/domain/entities/response/ResponseFilter";
import { useDebounce } from "~/v1/infrastructure/services";

export const useResponseFilterViewModel = ({
  datasetQuestions,
}: {
  datasetQuestions: Question[];
}) => {
  const debounce = useDebounce(500);

  const questionFilters = ref<ResponseFilterList>(
    new ResponseFilterList(datasetQuestions)
  );

  return { questionFilters, debounce };
};
