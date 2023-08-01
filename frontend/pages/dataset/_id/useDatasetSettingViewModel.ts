import { computed, onBeforeMount, ref } from "vue-demi";
import { useResolve } from "ts-injecty";
import { useRouter, useRoute } from "@nuxtjs/composition-api";
import { GetDatasetSettingsUseCase } from "~/v1/domain/usecases/get-dataset-settings-use-case";
import { useDatasetSetting } from "~/v1/infrastructure/storage/DatasetSettingStorage";
import { Dataset } from "~/v1/domain/entities/Dataset";
import { DATASET_API_ERRORS } from "~/v1/infrastructure/repositories";
import { Notification } from "@/models/Notifications";

export const useDatasetSettingViewModel = () => {
  const isLoadingDataset = ref(false);
  const router = useRouter();
  const route = useRoute();
  const datasetId = route.value.params.id;

  const { state: datasetSetting } = useDatasetSetting();
  const getDatasetSetting = useResolve(GetDatasetSettingsUseCase);

  const breadcrumbs = computed(() =>
    createBreadcrumbs(datasetSetting?.dataset)
  );

  const handleError = (response: string) => {
    let message = "";
    switch (response) {
      case DATASET_API_ERRORS.ERROR_FETCHING_DATASET_INFO:
        message = `Can't get dataset info for dataset_id: ${datasetId}`;
        break;
      case DATASET_API_ERRORS.ERROR_FETCHING_WORKSPACE_INFO:
        message = `Can't get workspace info for dataset_id: ${datasetId}`;
        break;
      default:
        message =
          "There was an error on fetching dataset info and workspace info. Please try again";
    }

    const paramsForNotification = {
      message,
      numberOfChars: message.length,
      type: "error",
    };

    Notification.dispatch("notify", paramsForNotification);
  };

  const createBreadcrumbs = (dataset: Dataset) => {
    return [
      { link: { name: "datasets" }, name: "Home" },
      {
        link: { path: `/datasets?workspace=${dataset.workspace}` },
        name: dataset.workspace,
      },
      {
        link: {
          name: null,
        },
        name: dataset.name,
      },
      {
        link: null,
        name: "settings",
      },
    ];
  };

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

  onBeforeMount(() => {
    loadDatasetSetting();
  });

  return { isLoadingDataset, breadcrumbs, datasetId, datasetSetting };
};
