import {
  computed,
  onBeforeMount,
  ref,
  useRouter,
} from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { useDatasetViewModel } from "../useDatasetViewModel";
import { GetDatasetByIdUseCase } from "@/v1/domain/usecases/get-dataset-by-id-use-case";
import { useDataset } from "@/v1/infrastructure/storage/DatasetStorage";
import { RecordCriteria } from "~/v1/domain/entities/record/RecordCriteria";
import { useRoutes } from "~/v1/infrastructure/services";
import { RecordStatus } from "~/v1/domain/entities/record/RecordAnswer";

export const useAnnotationModeViewModel = () => {
  const router = useRouter();
  const routes = useRoutes();
  const { state: dataset } = useDataset();
  const getDatasetUseCase = useResolve(GetDatasetByIdUseCase);

  const { datasetId, isLoadingDataset, handleError, createRootBreadCrumbs } =
    useDatasetViewModel();

  const breadcrumbs = computed(() => createRootBreadCrumbs(dataset));

  const recordCriteria = ref<RecordCriteria>(
    new RecordCriteria(
      datasetId,
      routes.getQueryParams<number>("_page"),
      routes.getQueryParams<RecordStatus>("_status"),
      routes.getQueryParams<RecordStatus>("_search"),
      routes.getQueryParams<string>("_metadata")?.split("+"),
      routes.getQueryParams<string>("_sort")?.split(","),
      routes.getQueryParams<string>("_similarity", true)
    )
  );

  routes.watchBrowserNavigation(() => {
    recordCriteria.value.complete(
      routes.getQueryParams<number>("_page"),
      routes.getQueryParams<RecordStatus>("_status"),
      routes.getQueryParams<RecordStatus>("_search"),
      routes.getQueryParams<string>("_metadata")?.split("+"),
      routes.getQueryParams<string>("_sort")?.split(","),
      routes.getQueryParams<string>("_similarity", true)
    );
  });

  const updateQueryParams = async () => {
    await routes.setQueryParams(
      {
        key: "_page",
        value: recordCriteria.value.committed.page.toString(),
      },
      {
        key: "_status",
        value: recordCriteria.value.committed.status,
      },
      {
        key: "_search",
        value: recordCriteria.value.committed.searchText,
      },
      {
        key: "_metadata",
        value: recordCriteria.value.committed.metadata.join("+"),
      },
      {
        key: "_sort",
        value: recordCriteria.value.committed.sortBy.join(","),
      },
      {
        key: "_similarity",
        value: recordCriteria.value.committed.similaritySearch.isCompleted
          ? JSON.stringify(recordCriteria.value.committed.similaritySearch)
          : undefined,
        encode: true,
      }
    );
  };

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
    loadDataset();
  });

  return {
    isLoadingDataset,
    recordCriteria,
    dataset,
    datasetId,
    breadcrumbs,
    updateQueryParams,
  };
};
