import { Dataset } from "../domain/entities/Dataset";
import { IDatasetsStorage } from "../domain/services/IDatasetsStorage";
import { useStoreFor } from "../store/create";

class Datasets {
  constructor(public readonly datasets: Dataset[] = []) {}
}

const useStoreForDatasets = useStoreFor<Datasets, IDatasetsStorage>(Datasets);
export const useDatasets = () => {
  const datasetsStore = useStoreForDatasets();

  const save = (datasets: Dataset[]) => {
    datasetsStore.save(new Datasets(datasets));
  };

  return { ...datasetsStore, save };
};
