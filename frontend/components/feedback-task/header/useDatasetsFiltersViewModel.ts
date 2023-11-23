import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "vue-demi";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { Question } from "~/v1/domain/entities/question/Question";
import { RecordCriteria } from "~/v1/domain/entities/record/RecordCriteria";
import { GetDatasetQuestionsFilterUseCase } from "~/v1/domain/usecases/get-dataset-questions-filter-use-case";
import { GetMetadataUseCase } from "~/v1/domain/usecases/get-metadata-use-case";
import { useRecords } from "~/v1/infrastructure/storage/RecordsStorage";

export const useDatasetsFiltersViewModel = ({
  recordCriteria,
}: {
  recordCriteria: RecordCriteria;
}) => {
  const { state: records } = useRecords();
  const datasetMetadataIsLoaded = ref(false);
  const datasetQuestionIsLoaded = ref(false);
  const datasetMetadata = ref<Metadata[]>([]);
  const datasetQuestions = ref<Question[]>([]);
  const getMetadataUseCase = useResolve(GetMetadataUseCase);
  const getQuestionsUseCase = useResolve(GetDatasetQuestionsFilterUseCase);

  const loadMetadata = async () => {
    try {
      datasetMetadata.value = await getMetadataUseCase.execute(
        recordCriteria.datasetId
      );
    } finally {
      datasetMetadataIsLoaded.value = true;
    }
  };

  const loadQuestions = async () => {
    try {
      datasetQuestions.value = await getQuestionsUseCase.execute(
        recordCriteria.datasetId
      );
    } finally {
      datasetQuestionIsLoaded.value = true;
    }
  };

  onBeforeMount(() => {
    loadMetadata();
    loadQuestions();
  });

  return {
    records,
    datasetMetadataIsLoaded,
    datasetQuestionIsLoaded,
    datasetMetadata,
    datasetQuestions,
  };
};
