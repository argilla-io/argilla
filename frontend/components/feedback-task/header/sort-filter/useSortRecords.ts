import { ref } from "vue-demi";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { Question } from "~/v1/domain/entities/question/Question";
import { SortList } from "~/v1/domain/entities/sort/SortList";
import { useFeatureToggle } from "~/v1/infrastructure/services";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";

export const useSortRecords = ({
  datasetMetadata,
  datasetQuestions,
}: {
  datasetMetadata: Metadata[];
  datasetQuestions: Question[];
}) => {
  const { getValue } = useFeatureToggle();
  const debounce = useDebounce(getValue("sort-delay", "integer") ?? 500);
  const categoriesSort = ref<SortList>(
    new SortList(datasetMetadata, datasetQuestions)
  );

  return { categoriesSort, debounce };
};
