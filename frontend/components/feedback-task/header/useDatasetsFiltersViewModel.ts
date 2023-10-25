import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { GetMetadataUseCase } from "~/v1/domain/usecases/get-metadata-use-case";
import { useRecords } from "~/v1/infrastructure/storage/RecordsStorage";

export const useDatasetsFiltersViewModel = () => {
  const { state: records } = useRecords();
  const datasetMetadata = ref<Metadata[]>([]);
  const getMetadataUseCase = useResolve(GetMetadataUseCase);

  const loadMetadata = async (datasetId: string) => {
    datasetMetadata.value = await getMetadataUseCase.execute(datasetId);
  };

  return { records, datasetMetadata, loadMetadata };
};
