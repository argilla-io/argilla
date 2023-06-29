import { GetDatasetsUseCase } from "~/v1/domain/usecases/get-datasets-use-case";
import { DatasetRepository } from "~/v1/infrastructure/DatasetRepository";
import { useDatasets } from "~/v1/infrastructure/DatasetsStorage";

export const useDatasetsViewModel = () => {
	const { state: datasets, ...datasetsStorage } = useDatasets();

	const loadDatasets = async (axios, fetchDatasets) => {
		const datasetRepository = new DatasetRepository(axios, fetchDatasets);
		const getDatasetsUseCase = new GetDatasetsUseCase(
			datasetRepository,
			datasetsStorage
		);

		await getDatasetsUseCase.execute();
	};

	return { loadDatasets, datasets };
};
