import { ref, useFetch } from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";
import { Question } from "~/v1/domain/entities/question/Question";
import { GetDatasetQuestionsFilterUseCase } from "~/v1/domain/usecases/get-dataset-questions-filter-use-case";

export const useDatasetQuestions = ({ dataset }: { dataset: Dataset }) => {
  const getQuestionsUseCase = useResolve(GetDatasetQuestionsFilterUseCase);
  const questions = ref<Question[]>([]);
  const isQuestionsLoading = ref(false);

  useFetch(async () => {
    try {
      isQuestionsLoading.value = true;

      const backendQuestions = await getQuestionsUseCase.execute(
        dataset.id,
        false
      );

      questions.value = [];

      for (const question of backendQuestions) {
        if (questions.value.some((q) => q.type.value === question.type.value))
          continue;

        questions.value.push(question);
      }
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
