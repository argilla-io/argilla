import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "@nuxtjs/composition-api";
import { GetDatasetProgressUseCase } from "@/v1/domain/usecases/get-dataset-progress-use-case";
import { Progress } from "~/v1/domain/entities/dataset/Progress";

export const useDatasetCardViewModel = (props) => {
  const datasetId = props.dataset.id;
  const completedPercent = ref("-");
  const total = ref(0);
  const progress = ref<Progress | null>(null);

  const getProgressUseCase = useResolve(GetDatasetProgressUseCase);

  onBeforeMount(async () => {
    progress.value = await getProgressUseCase.execute(datasetId);
    completedPercent.value = progress.value.percentage.completed;
    total.value = progress.value.total;
  });

  return {
    completedPercent,
    total,
  };
};
