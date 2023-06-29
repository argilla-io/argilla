import { Dataset } from "../domain/entities/Dataset";
import { IDatasetRepository } from "../domain/services/IDatasetRepository";
import { useStoreFor } from "../store/create";

export const useDataset = useStoreFor<Dataset, IDatasetRepository>(Dataset);
