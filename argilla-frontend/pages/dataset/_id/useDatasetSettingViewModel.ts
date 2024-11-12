import { computed, onBeforeMount, onBeforeUnmount, ref, watch } from "vue-demi";
import { useResolve } from "ts-injecty";
import { useDatasetViewModel } from "./useDatasetViewModel";
import { GetDatasetSettingsUseCase } from "~/v1/domain/usecases/dataset-setting/get-dataset-settings-use-case";
import { useDatasetSetting } from "~/v1/infrastructure/storage/DatasetSettingStorage";
import {
  useBeforeUnload,
  useRole,
  useRoutes,
  useTranslate,
} from "@/v1/infrastructure/services";
import { DatasetSetting } from "~/v1/domain/entities/dataset/DatasetSetting";
import { useNotifications } from "~/v1/infrastructure/services/useNotifications";

interface Tab {
  id:
    | "general"
    | "fields"
    | "questions"
    | "metadata"
    | "vector"
    | "danger-zone";
  name: string;
  component: string;
}

export const useDatasetSettingViewModel = () => {
  const notification = useNotifications();
  const routes = useRoutes();
  const beforeUnload = useBeforeUnload();
  const { t } = useTranslate();

  const { isAdminOrOwnerRole } = useRole();
  const { state: datasetSetting } = useDatasetSetting();
  const { datasetId, isLoadingDataset, handleError, createRootBreadCrumbs } =
    useDatasetViewModel();

  const getDatasetSetting = useResolve(GetDatasetSettingsUseCase);

  const tabs = ref<Tab[]>([]);

  const configureTabs = (datasetSettings: DatasetSetting) => {
    tabs.value.push({
      id: "general",
      name: t("general"),
      component: "SettingsInfo",
    });
    tabs.value.push({
      id: "fields",
      name: t("fields"),
      component: "SettingsFields",
    });
    tabs.value.push({
      id: "questions",
      name: t("questions"),
      component: "SettingsQuestions",
    });

    if (datasetSettings.hasMetadataProperties) {
      tabs.value.push({
        id: "metadata",
        name: t("metadata"),
        component: "SettingsMetadata",
      });
    }

    if (datasetSettings.hasVectors) {
      tabs.value.push({
        id: "vector",
        name: t("vectors"),
        component: "SettingsVectors",
      });
    }

    tabs.value.push({
      id: "danger-zone",
      name: t("dangerZone"),
      component: "SettingsDangerZone",
    });
  };

  const loadDatasetSetting = async () => {
    try {
      isLoadingDataset.value = true;

      const datasetSettings = await getDatasetSetting.execute(datasetId);
      configureTabs(datasetSettings);
    } catch (error) {
      handleError(error.response);

      routes.go("/");
    } finally {
      isLoadingDataset.value = false;
    }
  };

  const breadcrumbs = computed(() => {
    return [
      ...createRootBreadCrumbs(datasetSetting.dataset),
      {
        link: {},
        name: t("breadcrumbs.datasetSettings"),
      },
    ];
  });

  const goToDataset = () => {
    if (routes.previousRouteMatchWith(`${datasetId}/annotation-mode`)) {
      return routes.goBack();
    }

    routes.goToFeedbackTaskAnnotationPage(datasetId);
  };

  const goToTab = (id: Tab["id"]) => {
    document.getElementById(id)?.click();
  };

  const goToTabWithModification = () => {
    if (datasetSetting.isDatasetModified) return goToTab("general");
    if (datasetSetting.isFieldsModified) return goToTab("fields");
    if (datasetSetting.isQuestionsModified) return goToTab("questions");
    if (datasetSetting.isMetadataPropertiesModified) return goToTab("metadata");
    if (datasetSetting.isVectorsModified) return goToTab("vector");
  };

  const goToOutside = (next) => {
    if (datasetSetting.isModified) {
      return notification.notify({
        message: t("changes_no_submit"),
        buttonText: t("button.ignore_and_continue"),
        permanent: true,
        type: "warning",
        onClick() {
          next();
        },
        onClose() {
          goToTabWithModification();
        },
      });
    }

    next();
  };

  onBeforeMount(() => {
    loadDatasetSetting();
  });

  onBeforeUnmount(() => {
    beforeUnload.destroy();
  });

  watch(
    () => datasetSetting.isModified,
    (isModified) => {
      if (isModified) return beforeUnload.confirm();

      beforeUnload.destroy();
    }
  );

  const onTabChanged = async (tabId: Tab["id"]) => {
    await routes.setQueryParamsVirtually({ key: "tab", value: tabId });
  };

  const onTabLoaded = () => {
    const selectedTab = routes.getQueryParams<string>("tab") as Tab["id"];

    if (tabs.value.some((t) => t.id === selectedTab)) {
      goToTab(selectedTab);
    }
  };

  return {
    isLoadingDataset,
    breadcrumbs,
    tabs,
    isAdminOrOwnerRole,
    datasetId,
    datasetSetting,
    goToOutside,
    goToDataset,
    onTabChanged,
    onTabLoaded,
  };
};
