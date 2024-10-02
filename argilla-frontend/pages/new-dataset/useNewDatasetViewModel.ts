import { useResolve } from "ts-injecty";
import { ref } from "@nuxtjs/composition-api";
import { GetDatasetCreationUseCase } from "~/v1/domain/usecases/get-dataset-creation-use-case";

export const useNewDatasetViewModel = () => {
  const datasetId = ref();
  const datasetConfig = ref();
  const getDatasetCreationUseCase = useResolve(GetDatasetCreationUseCase);

  const getNewDatasetByRepoId = async (repositoryId: string) => {
    datasetId.value = repositoryId;
    datasetConfig.value = await getDatasetCreationUseCase.execute(repositoryId);
  };

  const changeSubset = (name: string) => {
    datasetConfig.value.changeSubset(name);
  };

  return {
    getNewDatasetByRepoId,
    datasetConfig,
    datasetId,
    changeSubset,
  };
};
