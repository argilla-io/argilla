import { useResolve } from "ts-injecty";
import { ref, useRoute, useContext } from "@nuxtjs/composition-api";
import { GetDatasetCreationUseCase } from "~/v1/domain/usecases/get-dataset-creation-use-case";

export const useNewDatasetViewModel = () => {
  const { error } = useContext();
  const datasetConfig = ref();
  const getDatasetCreationUseCase = useResolve(GetDatasetCreationUseCase);

  const getNewDatasetByRepoId = async (repositoryId: string) => {
    try {
      datasetConfig.value = await getDatasetCreationUseCase.execute(
        repositoryId
      );
    } catch (e) {
      error({ statusCode: 404, message: "Cannot fetch the dataset" });
    }
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
