import { GetDatasetsUseCase } from "~/v1/domain/usecases/get-datasets-use-case";
import { DatasetRepository } from "~/v1/infrastructure/DatasetRepository";
import { useDatasets } from "~/v1/infrastructure/DatasetStorage";

export const useDatasetsViewModel = () => {
	const { state: datasets, ...service } = useDatasets();

	const loadDatasets = async (axios, fetchDatasets) => {
		const datasetRepository = new DatasetRepository(axios, fetchDatasets);
		const getDatasetsUseCase = new GetDatasetsUseCase(
			datasetRepository,
			service
		);

		await getDatasetsUseCase.execute();
	};

	return { loadDatasets, datasets };
};
