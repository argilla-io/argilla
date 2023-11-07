import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { Question } from "~/v1/domain/entities/question/Question";
import { GetDatasetQuestionsUseCase } from "~/v1/domain/usecases/get-dataset-questions-use-case";
import { GetMetadataUseCase } from "~/v1/domain/usecases/get-metadata-use-case";
import { useRecords } from "~/v1/infrastructure/storage/RecordsStorage";

export const useDatasetsFiltersViewModel = () => {
  const { state: records } = useRecords();
  const datasetMetadata = ref<Metadata[]>([]);
  const datasetQuestions = ref<Question[]>([]);
  const getMetadataUseCase = useResolve(GetMetadataUseCase);
  const getQuestionsUseCase = useResolve(GetDatasetQuestionsUseCase);

  const loadMetadata = async (datasetId: string) => {
    datasetMetadata.value = await getMetadataUseCase.execute(datasetId);
  };

  const loadQuestions = async (datasetId: string) => {
    datasetQuestions.value = await getQuestionsUseCase.execute(datasetId);
  };

  return {
    records,
    datasetMetadata,
    datasetQuestions,
    loadMetadata,
    loadQuestions,
  };
};
