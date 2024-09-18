import { useResolve } from "ts-injecty";
import { ref, useFetch } from "@nuxtjs/composition-api";
import { GetDatasetsUseCase } from "@/v1/domain/usecases/get-datasets-use-case";
import { useDatasets } from "~/v1/infrastructure/storage/DatasetsStorage";
import { useFocusTab } from "~/v1/infrastructure/services";

export const useDatasetsViewModel = () => {
  const isLoadingDatasets = ref(false);
  const { state: datasets } = useDatasets();
  const getDatasetsUseCase = useResolve(GetDatasetsUseCase);

  useFocusTab(async () => {
    await onLoadDatasets();
  });

  useFetch(() => {
    loadDatasets();
  });

  const onLoadDatasets = async () => {
    await getDatasetsUseCase.execute();
  };

  const loadDatasets = async () => {
    isLoadingDatasets.value = true;

    await onLoadDatasets();

    isLoadingDatasets.value = false;
  };

  return { datasets, isLoadingDatasets };
};
