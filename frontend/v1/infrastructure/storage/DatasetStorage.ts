import { Dataset } from "@/v1/domain/entities/Dataset";
import { IDatasetStorage } from "@/v1/domain/services/IDatasetStorage";
import { useStoreFor } from "@/v1/store/create";

const useStoreForDataset = useStoreFor<Dataset, IDatasetStorage>(Dataset);
export const useDataset = () => useStoreForDataset();
