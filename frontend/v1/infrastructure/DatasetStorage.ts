import { Dataset } from "../domain/entities/Dataset";
import { IDatasetStorage } from "../domain/services/IDatasetStorage";
import { useStoreFor } from "../store/create";

const useDatasetStore = useStoreFor(Dataset);

export const useDataset = () => {
	const internalStore = useDatasetStore();

	return { ...internalStore } as IDatasetStorage & typeof internalStore;
};
