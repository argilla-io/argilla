import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { GetMetadataUseCase } from "~/v1/domain/usecases/get-metadata-use-case";

export const useDatasetsFiltersViewModel = () => {
  const datasetsMetadata = ref<Metadata[]>([]);
  const getMetadataUseCase = useResolve(GetMetadataUseCase);

  const loadMetadata = async (datasetId: string) => {
    datasetsMetadata.value = await getMetadataUseCase.execute(datasetId);
  };

  return { datasetsMetadata, loadMetadata };
};
