import { Dataset } from "~/v1/domain/entities/dataset/Dataset";
import { IDatasetsStorage } from "@/v1/domain/services/IDatasetsStorage";
import { useStoreFor } from "@/v1/store/create";

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
