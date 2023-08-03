import { computed, onBeforeMount } from "vue-demi";
import { useResolve } from "ts-injecty";
import { useRouter, useContext } from "@nuxtjs/composition-api";
import { useDatasetViewModel } from "./useDatasetViewModel";
import { GetDatasetSettingsUseCase } from "~/v1/domain/usecases/dataset-setting/get-dataset-settings-use-case";
import { useDatasetSetting } from "~/v1/infrastructure/storage/DatasetSettingStorage";

export const useDatasetSettingViewModel = () => {
  const router = useRouter();
  const { $auth } = useContext();
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

  const isAdminOrOwnerRole = computed(() => {
    const role = $auth.user.role;
    return role === "admin" || role === "owner";
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
