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
import { useRoutes, useUser } from "~/v1/infrastructure/services";
import { RecordStatus } from "~/v1/domain/entities/record/RecordAnswer";

export const useAnnotationModeViewModel = () => {
  const router = useRouter();
  const routes = useRoutes();
  const { user } = useUser();
  const { state: dataset } = useDataset();
  const getDatasetUseCase = useResolve(GetDatasetByIdUseCase);

  const { datasetId, isLoadingDataset, handleError, createRootBreadCrumbs } =
    useDatasetViewModel();

  const breadcrumbs = computed(() => createRootBreadCrumbs(dataset));

  const recordCriteria = ref<RecordCriteria>(
    new RecordCriteria(
      datasetId,
      routes.getQueryParams<string>("page"),
      routes.getQueryParams<RecordStatus>("status"),
      routes.getQueryParams<string>("search"),
      routes.getQueryParams<string>("metadata"),
      routes.getQueryParams<string>("sort"),
      routes.getQueryParams<string>("response"),
      routes.getQueryParams<string>("suggestion"),
      routes.getQueryParams<string>("similarity")
    )
  );

  routes.watchBrowserNavigation(() => {
    recordCriteria.value.complete(
      routes.getQueryParams<string>("page"),
      routes.getQueryParams<RecordStatus>("status"),
      routes.getQueryParams<string>("search"),
      routes.getQueryParams<string>("metadata"),
      routes.getQueryParams<string>("sort"),
      routes.getQueryParams<string>("response"),
      routes.getQueryParams<string>("suggestion"),
      routes.getQueryParams<string>("similarity")
    );
  });

  const updateQueryParams = async () => {
    await routes.setQueryParams(
      {
        key: "page",
        value: recordCriteria.value.committed.page.urlParams,
      },
      {
        key: "status",
        value: recordCriteria.value.committed.status,
      },
      {
        key: "search",
        value: recordCriteria.value.committed.searchText.urlParams,
      },
      {
        key: "metadata",
        value: recordCriteria.value.committed.metadata.urlParams,
      },
      {
        key: "sort",
        value: recordCriteria.value.committed.sortBy.urlParams,
      },
      {
        key: "response",
        value: recordCriteria.value.committed.response.urlParams,
      },
      {
        key: "suggestion",
        value: recordCriteria.value.committed.suggestion.urlParams,
      },
      {
        key: "similarity",
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
    user,
  };
};
