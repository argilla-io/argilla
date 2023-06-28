import { Dataset } from "../domain/entities/Dataset";
import { useStoreFor } from "../store/create";

class Datasets {
  constructor(public readonly datasets: Dataset[]) {}
}

const useDatasetsInternal = useStoreFor(Datasets);

export const useDatasets = () => {
  const internalStore = useDatasetsInternal();

  const save = (datasets: Dataset[]) => {
    internalStore.save(new Datasets(datasets));
  };

  return { ...internalStore, save };
};
