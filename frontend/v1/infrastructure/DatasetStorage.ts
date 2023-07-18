import { Dataset } from "../domain/entities/Dataset";
import { IDatasetStorage } from "../domain/services/IDatasetStorage";
import { useStoreFor } from "../store/create";

const useStoreForDataset = useStoreFor<Dataset, IDatasetStorage>(Dataset);
export const useDataset = () => useStoreForDataset();
