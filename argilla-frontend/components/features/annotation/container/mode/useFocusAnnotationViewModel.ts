import { useResolve } from "ts-injecty";
import { ref, getCurrentInstance, onMounted, computed } from "vue-demi";
import { Record } from "~/v1/domain/entities/record/Record";
import { DiscardRecordUseCase } from "~/v1/domain/usecases/discard-record-use-case";
import { SubmitRecordUseCase } from "~/v1/domain/usecases/submit-record-use-case";
import { SaveDraftUseCase } from "~/v1/domain/usecases/save-draft-use-case";
import { useSpeech } from "~/v1/infrastructure/services/useSpeech";
import { RecordCriteria } from "~/v1/domain/entities/record/RecordCriteria";
import { Records } from "~/v1/domain/entities/record/Records";

export const useFocusAnnotationViewModel = ({
  recordCriteria,
  records,
}: {
  recordCriteria: RecordCriteria;
  records: Records;
}) => {
  const isDraftSaving = ref(false);
  const isDiscarding = ref(false);
  const isSubmitting = ref(false);
  const discardUseCase = useResolve(DiscardRecordUseCase);
  const submitUseCase = useResolve(SubmitRecordUseCase);
  const saveDraftUseCase = useResolve(SaveDraftUseCase);
  const instance = getCurrentInstance().proxy;
  const speech = useSpeech();

  const record = computed(() =>
    records.getRecordOn(recordCriteria.committed.page)
  );

  onMounted(() => {
    speech.waitCommands({
      SelectOption: (optionNumber) => {
        record.value.questions.forEach((question) => {
          question.answerByIndex(optionNumber - 1);
        });
      },
      Submit: () => {
        submit(record.value);

        instance.$emit("on-submit-responses");
      },
    });
  });

  const discard = async (record: Record) => {
    try {
      isDiscarding.value = true;

      await discardUseCase.execute(record);
    } catch {
    } finally {
      isDiscarding.value = false;
    }
  };

  const submit = async (record: Record) => {
    try {
      isSubmitting.value = true;

      await submitUseCase.execute(record);
    } catch {
    } finally {
      isSubmitting.value = false;
    }
  };

  const saveAsDraft = async (record: Record) => {
    try {
      isDraftSaving.value = true;

      await saveDraftUseCase.execute(record);
    } catch {
    } finally {
      isDraftSaving.value = false;
    }
  };

  return {
    isDraftSaving,
    isDiscarding,
    isSubmitting,
    submit,
    discard,
    saveAsDraft,
  };
};
