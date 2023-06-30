import { Dataset } from "../domain/entities/Dataset";
import { IDatasetStorage } from "../domain/services/IDatasetStorage";
import { useStoreFor } from "../store/create";

export const useDataset = useStoreFor<Dataset, IDatasetStorage>(Dataset);
