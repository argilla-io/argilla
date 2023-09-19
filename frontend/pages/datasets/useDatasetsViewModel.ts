import { useResolve } from "ts-injecty";
import { ref, useFetch } from "@nuxtjs/composition-api";
import { GetDatasetsUseCase } from "@/v1/domain/usecases/get-datasets-use-case";
import { useDatasets } from "~/v1/infrastructure/storage/DatasetsStorage";

export const useDatasetsViewModel = () => {
  const isLoadingDatasets = ref(false);
  const { state: datasets } = useDatasets();
  const getDatasetsUseCase = useResolve(GetDatasetsUseCase);

  useFetch(() => {
    loadDatasets();
  });

  const loadDatasets = async () => {
    isLoadingDatasets.value = true;

    await getDatasetsUseCase.execute();

    isLoadingDatasets.value = false;
  };

  return { datasets, isLoadingDatasets };
};
