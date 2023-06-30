import { useResolve } from "ts-injecty";
import { GetDatasetsUseCase } from "@/v1/domain/usecases/get-datasets-use-case";
import { useDatasets } from "@/v1/infrastructure/DatasetsStorage";

export const useDatasetsViewModel = () => {
  const { state: datasets } = useDatasets();
  const getDatasetsUseCase = useResolve(GetDatasetsUseCase);

  const loadDatasets = () => {
    getDatasetsUseCase.execute();
  };

  return { loadDatasets, datasets };
};
