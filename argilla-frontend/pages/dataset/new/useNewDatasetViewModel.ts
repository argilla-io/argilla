import { useResolve } from "ts-injecty";
import { ref } from "@nuxtjs/composition-api";
import { GetDatasetCreationUseCase } from "~/v1/domain/usecases/get-dataset-creation-use-case";
import { useRoute } from "@nuxtjs/composition-api";

export const useNewDatasetViewModel = () => {
  const datasetConfig = ref();
  const getDatasetCreationUseCase = useResolve(GetDatasetCreationUseCase);

  const getNewDatasetByRepoId = async (repositoryId: string) => {
    datasetConfig.value = await getDatasetCreationUseCase.execute(
      decodeURI(repositoryId)
    );
  };

  const getNewDatasetByRepoIdFromUrl = async () => {
    const repositoryId = useRoute().value.params.id;
    await getNewDatasetByRepoId(decodeURI(repositoryId));
  };

  const changeSubset = (name: string) => {
    datasetConfig.value.changeSubset(name);
  };

  return {
    getNewDatasetByRepoId,
    getNewDatasetByRepoIdFromUrl,
    changeSubset,
    datasetConfig,
  };
};
