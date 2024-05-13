import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "vue-demi";
import { Field } from "~/v1/domain/entities/field/Field";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { Question } from "~/v1/domain/entities/question/Question";
import { RecordCriteria } from "~/v1/domain/entities/record/RecordCriteria";
import { GetDatasetQuestionsFilterUseCase } from "~/v1/domain/usecases/get-dataset-questions-filter-use-case";
import { GetFieldsUseCase } from "~/v1/domain/usecases/get-fields-use-case";
import { GetMetadataUseCase } from "~/v1/domain/usecases/get-metadata-use-case";

export const useDatasetsFiltersViewModel = ({
  recordCriteria,
}: {
  recordCriteria: RecordCriteria;
}) => {
  const datasetMetadataIsLoaded = ref(false);
  const datasetQuestionIsLoaded = ref(false);
  const datasetMetadata = ref<Metadata[]>([]);
  const datasetQuestions = ref<Question[]>([]);
  const datasetFields = ref<Field[]>([]);
  const getMetadataUseCase = useResolve(GetMetadataUseCase);
  const getQuestionsUseCase = useResolve(GetDatasetQuestionsFilterUseCase);
  const getFieldsUseCase = useResolve(GetFieldsUseCase);

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

  const loadFields = async () => {
    try {
      datasetFields.value = await getFieldsUseCase.execute(
        recordCriteria.datasetId
      );
    } catch {}
  };

  onBeforeMount(() => {
    loadMetadata();
    loadQuestions();
    loadFields();
  });

  return {
    datasetMetadataIsLoaded,
    datasetQuestionIsLoaded,
    datasetMetadata,
    datasetQuestions,
    datasetFields,
  };
};
