import {
  computed,
  onBeforeMount,
  ref,
  useRoute,
  useRouter,
} from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { createBreadcrumbs } from "../breadcrumbs";
import { useDatasetViewModel } from "../useDatasetViewModel";
import { Notification } from "@/models/Notifications";
import { GetDatasetByIdUseCase } from "@/v1/domain/usecases/get-dataset-by-id-use-case";
import { DATASET_API_ERRORS } from "@/v1/infrastructure/repositories/DatasetRepository";
import { useDataset } from "@/v1/infrastructure/storage/DatasetStorage";
import {
  useEvents,
  UpdateMetricsEventHandler,
} from "~/v1/infrastructure/events";

export const useAnnotationModeViewModel = () => {
  const router = useRouter();
  const { state: dataset } = useDataset();
  const getDatasetUseCase = useResolve(GetDatasetByIdUseCase);

  const { datasetId, isLoadingDataset, handleError, createRootBreadCrumbs } =
    useDatasetViewModel();

  const breadcrumbs = computed(() => createRootBreadCrumbs(dataset));

  const loadDataset = async () => {
    try {
      isLoadingDataset.value = true;

      await getDatasetUseCase.execute(datasetId);
    } catch (error) {
      handleError(error.response);

      router.push("/");
    } finally {
      isLoadingDataset.value = false;
    }
  };

  onBeforeMount(() => {
    useEvents(() => {
      new UpdateMetricsEventHandler();
    });

    loadDataset();
  });

  return { dataset, datasetId, isLoadingDataset, loadDataset, breadcrumbs };
};
