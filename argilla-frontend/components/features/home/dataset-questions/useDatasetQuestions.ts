import { ref, useFetch } from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";
import { Question } from "~/v1/domain/entities/question/Question";
import { GetDatasetQuestionsGroupedUseCase } from "~/v1/domain/usecases/get-dataset-questions-grouped-use-case";

export const useDatasetQuestions = ({ dataset }: { dataset: Dataset }) => {
  const getQuestionsUseCase = useResolve(GetDatasetQuestionsGroupedUseCase);
  const questions = ref<Question[]>([]);
  const isQuestionsLoading = ref(false);

  useFetch(async () => {
    try {
      isQuestionsLoading.value = true;

      questions.value = await getQuestionsUseCase.execute(dataset.id);
    } catch {
    } finally {
      isQuestionsLoading.value = false;
    }
  });

  return {
    questions,
    isQuestionsLoading,
  };
};
