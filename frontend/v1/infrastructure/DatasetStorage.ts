import { Dataset } from "../domain/entities/Dataset";
import { useStoreFor } from "../store/create";

class Datasets {
	constructor(public readonly datasets: Dataset[]) {}
}

const useDatasetsStore = useStoreFor(Datasets);

export const useDatasets = () => {
	const internalStore = useDatasetsStore();

	const save = (datasets: Dataset[]) => {
		internalStore.save(new Datasets(datasets));
	};

	return { ...internalStore, save };
};
