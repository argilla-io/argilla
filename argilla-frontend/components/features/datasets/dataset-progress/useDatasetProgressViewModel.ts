import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "@nuxtjs/composition-api";
import { GetDatasetProgressUseCase } from "@/v1/domain/usecases/get-dataset-progress-use-case";
import { useTranslate } from "~/v1/infrastructure/services/useTranslate";
import { Progress } from "~/v1/domain/entities/dataset/Progress";

export const useDatasetProgressViewModel = ({
  datasetId,
}: {
  datasetId: string;
}) => {
  const { t } = useTranslate();
  const isLoaded = ref(false);
  const progress = ref<Progress | null>(null);
  const progressRanges = ref([]);

  const getProgressUseCase = useResolve(GetDatasetProgressUseCase);

  onBeforeMount(async () => {
    progress.value = await getProgressUseCase.execute(datasetId);

    progressRanges.value = [
      {
        id: "completed",
        name: t("datasets.completed"),
        color:
          "linear-gradient(90deg, var(--fg-tertiary) 0%, var(--fg-primary) 100%)",
        value: progress.value.completed,
        tooltip: `${progress.value.completed}/${progress.value.total}`,
      },
      {
        id: "pending",
        name: t("datasets.left"),
        color: "var(--bg-solid-grey-3)",
        value: progress.value.pending,
        tooltip: `${progress.value.pending}/${progress.value.total}`,
      },
    ];

    isLoaded.value = true;
  });

  return {
    isLoaded,
    progress,
    progressRanges,
  };
};
