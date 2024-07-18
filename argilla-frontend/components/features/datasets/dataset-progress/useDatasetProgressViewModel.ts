import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "@nuxtjs/composition-api";
import { GetDatasetProgressUseCase } from "@/v1/domain/usecases/get-dataset-progress-use-case";
import { useTranslate } from "~/v1/infrastructure/services/useTranslate";
import { useTeamProgress } from "~/v1/infrastructure/storage/TeamProgressStorage";

export const useDatasetProgressViewModel = ({
  datasetId,
}: {
  datasetId: string;
}) => {
  const t = useTranslate();
  const isLoaded = ref(false);
  const progressRanges = ref([]);

  const { state: progress } = useTeamProgress();
  const getProgressUseCase = useResolve(GetDatasetProgressUseCase);

  onBeforeMount(async () => {
    await getProgressUseCase.execute(datasetId);

    progressRanges.value = [
      {
        id: "completed",
        name: t("datasets.completed"),
        color: "linear-gradient(90deg, #6A6A6C 0%, #252626 100%)",
        value: progress.completed,
        tooltip: `${progress.completed}/${progress.total}`,
      },
      {
        id: "pending",
        name: t("datasets.left"),
        color: "#e6e6e6",
        value: progress.pending,
        tooltip: `${progress.pending}/${progress.total}`,
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
