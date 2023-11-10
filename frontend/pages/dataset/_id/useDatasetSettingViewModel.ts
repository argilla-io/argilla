import { computed, onBeforeMount, ref } from "vue-demi";
import { useResolve } from "ts-injecty";
import { useRouter } from "@nuxtjs/composition-api";
import { useDatasetViewModel } from "./useDatasetViewModel";
import { GetDatasetSettingsUseCase } from "~/v1/domain/usecases/dataset-setting/get-dataset-settings-use-case";
import { useDatasetSetting } from "~/v1/infrastructure/storage/DatasetSettingStorage";
import { useRole } from "@/v1/infrastructure/services";
import { DatasetSetting } from "~/v1/domain/entities/DatasetSetting";

interface Tab {
  id: string;
  name: string;
  component: string;
}

export const useDatasetSettingViewModel = () => {
  const router = useRouter();
  const { isAdminOrOwnerRole } = useRole();
  const { state: datasetSetting } = useDatasetSetting();
  const getDatasetSetting = useResolve(GetDatasetSettingsUseCase);

  const tabs = ref<Tab[]>([]);

  const configureTabs = (datasetSettings: DatasetSetting) => {
    tabs.value.push({ id: "info", name: "Info", component: "SettingsInfo" });
    tabs.value.push({
      id: "fields",
      name: "Fields",
      component: "SettingsFields",
    });
    tabs.value.push({
      id: "questions",
      name: "Questions",
      component: "SettingsQuestions",
    });

    if (datasetSettings.hasMetadataProperties) {
      tabs.value.push({
        id: "metadata",
        name: "Metadata",
        component: "SettingsMetadata",
      });
    }

    if (datasetSettings.hasVectors) {
      tabs.value.push({
        id: "vector",
        name: "Vectors",
        component: "SettingsVectors",
      });
    }

    tabs.value.push({
      id: "danger-zone",
      name: "Danger zone",
      component: "settingsDangerZone",
    });
  };

  const { datasetId, isLoadingDataset, handleError, createRootBreadCrumbs } =
    useDatasetViewModel();

  const loadDatasetSetting = async () => {
    try {
      isLoadingDataset.value = true;

      const datasetSettings = await getDatasetSetting.execute(datasetId);
      configureTabs(datasetSettings);
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

  return {
    isLoadingDataset,
    breadcrumbs,
    tabs,
    isAdminOrOwnerRole,
    datasetId,
    datasetSetting,
  };
};
