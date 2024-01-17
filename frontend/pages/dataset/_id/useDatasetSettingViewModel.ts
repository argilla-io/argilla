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
import { DatasetSetting } from "~/v1/domain/entities/DatasetSetting";
import { Notification } from "~/models/Notifications";

interface Tab {
  id: "info" | "fields" | "questions" | "metadata" | "vector" | "danger-zone";
  name: string;
  component: string;
}

export const useDatasetSettingViewModel = () => {
  const routes = useRoutes();
  const beforeUnload = useBeforeUnload();
  const t = useTranslate();

  const { isAdminOrOwnerRole } = useRole();
  const { state: datasetSetting } = useDatasetSetting();
  const { datasetId, isLoadingDataset, handleError, createRootBreadCrumbs } =
    useDatasetViewModel();

  const getDatasetSetting = useResolve(GetDatasetSettingsUseCase);

  const tabs = ref<Tab[]>([]);

  const configureTabs = (datasetSettings: DatasetSetting) => {
    tabs.value.push({ id: "info", name: "Info", component: "SettingsInfo" });
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

  const onGoToDataset = () => {
    if (routes.previousRouteMatchWith(datasetId)) return routes.goBack();

    routes.goToFeedbackTaskAnnotationPage(datasetId);
  };

  const goToTabWithModification = () => {
    const goToTab = (id: Tab["id"]) => {
      document.getElementById(id).click();
    };

    if (datasetSetting.isDatasetModified) return goToTab("info");
    if (datasetSetting.isFieldsModified) return goToTab("fields");
    if (datasetSetting.isQuestionsModified) return goToTab("questions");
    if (datasetSetting.isMetadataPropertiesModified) return goToTab("metadata");
    if (datasetSetting.isVectorsModified) return goToTab("vector");
  };

  const goToDataset = () => {
    if (datasetSetting.isModified) {
      return Notification.dispatch("notify", {
        message: t("changes_no_submit"),
        buttonText: t("button.ignore_and_continue"),
        permanent: true,
        type: "warning",
        onClick() {
          onGoToDataset();
        },
        onClose() {
          goToTabWithModification();
        },
      });
    }

    onGoToDataset();
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

  return {
    isLoadingDataset,
    breadcrumbs,
    tabs,
    isAdminOrOwnerRole,
    datasetId,
    datasetSetting,
    goToDataset,
  };
};
