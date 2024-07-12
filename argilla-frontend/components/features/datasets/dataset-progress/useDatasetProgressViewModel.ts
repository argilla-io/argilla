import { useResolve } from "ts-injecty";
import { ref, useFetch } from "@nuxtjs/composition-api";
import { GetDatasetProgressUseCase } from "@/v1/domain/usecases/get-dataset-progress-use-case";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";
import { useTranslate } from "~/v1/infrastructure/services/useTranslate";
import { Progress } from "~/v1/domain/entities/dataset/Progress";

export const useDatasetProgressViewModel = ({
  dataset,
}: {
  dataset: Dataset;
}) => {
  const getProgressUseCase = useResolve(GetDatasetProgressUseCase);
  const progress = ref<Progress | null>(null);
  const progressRanges = ref([]);

  const t = useTranslate();

  useFetch(async () => {
    try {
      progress.value = await getProgressUseCase.execute(dataset.id);

      progressRanges.value = [
        {
          id: "completed",
          name: t("datasets.completed"),
          color: "linear-gradient(90deg, #6A6A6C 0%, #252626 100%)",
          value: progress.value.completed,
          tooltip: `${progress.value.completed}/${progress.value.total}`,
        },
        {
          id: "pending",
          name: t("datasets.left"),
          color: "#e6e6e6",
          value: progress.value.pending,
          tooltip: `${progress.value.pending}/${progress.value.total}`,
        },
      ];
    } catch {}
  });

  return {
    progress,
    progressRanges,
  };
};
