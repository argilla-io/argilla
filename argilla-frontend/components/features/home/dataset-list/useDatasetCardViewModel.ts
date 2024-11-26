import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "@nuxtjs/composition-api";
import { GetDatasetProgressUseCase } from "@/v1/domain/usecases/get-dataset-progress-use-case";
import { Progress } from "~/v1/domain/entities/dataset/Progress";
import { useRoutes } from "@/v1/infrastructure/services";

export const useDatasetCardViewModel = (props) => {
  const { getDatasetLink, goToSetting } = useRoutes();

  const datasetId = props.dataset.id;
  const completedPercent = ref("-");
  const users = ref([]);
  const total = ref(0);
  const progress = ref<Progress | null>(null);

  const getProgressUseCase = useResolve(GetDatasetProgressUseCase);

  onBeforeMount(async () => {
    progress.value = await getProgressUseCase.execute(datasetId);
    completedPercent.value = progress.value.percentage.completed;
    total.value = progress.value.total;
    users.value = progress.value.users;
  });

  return {
    getDatasetLink,
    goToSetting: () => goToSetting(datasetId),

    completedPercent,
    total,
    users,
  };
};
