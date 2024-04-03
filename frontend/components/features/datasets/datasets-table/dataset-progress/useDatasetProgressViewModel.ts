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
    if (!dataset.isFeedbackTask) return;

    try {
      progress.value = await getProgressUseCase.execute(dataset.id);

      progressRanges.value = [
        {
          id: "submitted",
          name: t("datasets.submitted"),
          color: "#0508D9",
          value: progress.value.submitted,
          tooltip: `${progress.value.submitted} / ${progress.value.total}`,
        },
        {
          id: "pending",
          name: t("datasets.pending"),
          color: "#f2f2f2",
          value: progress.value.remaining,
          tooltip: `${progress.value.remaining} / ${progress.value.total}`,
        },
      ];
    } catch {}
  });

  return {
    progress,
    progressRanges,
  };
};
