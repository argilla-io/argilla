import { computed, onBeforeMount } from "vue-demi";
import { useResolve } from "ts-injecty";
import { useRouter } from "@nuxtjs/composition-api";
import { useDatasetViewModel } from "./useDatasetViewModel";
import { GetDatasetSettingsUseCase } from "~/v1/domain/usecases/get-dataset-settings-use-case";
import { useDatasetSetting } from "~/v1/infrastructure/storage/DatasetSettingStorage";

export const useDatasetSettingViewModel = () => {
  const router = useRouter();
  const { state: datasetSetting } = useDatasetSetting();
  const getDatasetSetting = useResolve(GetDatasetSettingsUseCase);

  const { datasetId, isLoadingDataset, handleError, createRootBreadCrumbs } =
    useDatasetViewModel();

  const loadDatasetSetting = async () => {
    try {
      isLoadingDataset.value = true;

      await getDatasetSetting.execute(datasetId);
    } catch (error) {
      handleError(error.response);

      router.push("/");
    } finally {
      isLoadingDataset.value = false;
    }
  };

  const breadcrumbs = computed(() => {
    return [
      ...createRootBreadCrumbs(datasetSetting.dataset),
      {
        link: {},
        name: "settings",
      },
    ];
  });

  onBeforeMount(() => {
    loadDatasetSetting();
  });

  return { isLoadingDataset, breadcrumbs, datasetId, datasetSetting };
};
