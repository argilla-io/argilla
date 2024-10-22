import { useResolve } from "ts-injecty";
import { ref, useFetch } from "@nuxtjs/composition-api";
import { useRoutes, useFocusTab } from "~/v1/infrastructure/services";
import { GetDatasetCreationUseCase } from "~/v1/domain/usecases/get-dataset-creation-use-case";
import { GetDatasetsUseCase } from "@/v1/domain/usecases/get-datasets-use-case";
import { useDatasets } from "~/v1/infrastructure/storage/DatasetsStorage";

export const useHomeViewModel = () => {
  const isLoadingDatasets = ref(false);
  const { goToImportDatasetFromHub } = useRoutes();
  const { state: datasets } = useDatasets();
  const getDatasetsUseCase = useResolve(GetDatasetsUseCase);
  const getDatasetCreationUseCase = useResolve(GetDatasetCreationUseCase);

  useFocusTab(async () => {
    await onLoadDatasets();
  });

  useFetch(() => {
    loadDatasets();
  });

  const getNewDatasetByRepoId = async (repositoryId: string) => {
    await getDatasetCreationUseCase.execute(repositoryId);

    goToImportDatasetFromHub(repositoryId);
  };

  const onLoadDatasets = async () => {
    await getDatasetsUseCase.execute();
  };

  const loadDatasets = async () => {
    isLoadingDatasets.value = true;

    await onLoadDatasets();

    isLoadingDatasets.value = false;
  };

  return {
    datasets,
    isLoadingDatasets,
    getNewDatasetByRepoId,
  };
};
