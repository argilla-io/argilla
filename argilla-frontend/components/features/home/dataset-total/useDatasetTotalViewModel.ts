import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "@nuxtjs/composition-api";
import { GetDatasetProgressUseCase } from "@/v1/domain/usecases/get-dataset-progress-use-case";
import { Progress } from "~/v1/domain/entities/dataset/Progress";

export const useDatasetTotalViewModel = ({
  datasetId,
}: {
  datasetId: string;
}) => {
  const isLoaded = ref(false);
  const totalRecords = ref(0);

  const getProgressUseCase = useResolve(GetDatasetProgressUseCase);

  onBeforeMount(async () => {
    const progress: Progress = await getProgressUseCase.execute(datasetId);
    totalRecords.value = progress.total;

    isLoaded.value = true;
  });

  return {
    totalRecords,
  };
};
