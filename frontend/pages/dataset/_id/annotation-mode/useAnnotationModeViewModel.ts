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
      routes.getQueryParams<string>("_metadata"),
      routes.getQueryParams<string>("_sort"),
      routes.getQueryParams<string>("_response"),
      routes.getQueryParams<string>("_suggestion")?.split("+"),
      routes.getQueryParams<string>("_similarity")
    )
  );

  routes.watchBrowserNavigation(() => {
    recordCriteria.value.complete(
      routes.getQueryParams<number>("_page"),
      routes.getQueryParams<RecordStatus>("_status"),
      routes.getQueryParams<RecordStatus>("_search"),
      routes.getQueryParams<string>("_metadata"),
      routes.getQueryParams<string>("_sort"),
      routes.getQueryParams<string>("_response"),
      routes.getQueryParams<string>("_suggestion")?.split("+"),
      routes.getQueryParams<string>("_similarity")
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
        value: recordCriteria.value.committed.metadata.urlParams,
      },
      {
        key: "_sort",
        value: recordCriteria.value.committed.sortBy.urlParams,
      },
      {
        key: "_response",
        value: recordCriteria.value.committed.response.urlParams,
      },
      {
        key: "_suggestion",
        value: recordCriteria.value.committed.suggestion.join("+"),
      },
      {
        key: "_similarity",
        value: recordCriteria.value.committed.similaritySearch.urlParams,
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
