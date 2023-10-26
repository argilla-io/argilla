import { computed, onBeforeMount } from "vue-demi";
import { useResolve } from "ts-injecty";
import { useRouter } from "@nuxtjs/composition-api";
import { useDatasetViewModel } from "./useDatasetViewModel";
import { GetDatasetSettingsUseCase } from "~/v1/domain/usecases/dataset-setting/get-dataset-settings-use-case";
import { useDatasetSetting } from "~/v1/infrastructure/storage/DatasetSettingStorage";
import { useRole } from "@/v1/infrastructure/services";

export const useDatasetSettingViewModel = () => {
  const router = useRouter();
  const { isAdminOrOwnerRole } = useRole();
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

  const tabs = [
    { id: "info", name: "Info", component: "settingsInfo" },
    { id: "fields", name: "Fields", component: "settingsFields" },
    { id: "questions", name: "Questions", component: "settingsQuestions" },
    {
      id: "vector",
      name: "Vectors",
      component: "SettingsVectors",
    },
    {
      id: "danger-zone",
      name: "Danger zone",
      component: "settingsDangerZone",
    },
  ];

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

  return {
    isLoadingDataset,
    breadcrumbs,
    tabs,
    isAdminOrOwnerRole,
    datasetId,
    datasetSetting,
  };
};
