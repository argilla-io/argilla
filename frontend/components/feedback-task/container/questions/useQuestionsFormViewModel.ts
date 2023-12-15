import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Record } from "~/v1/domain/entities/record/Record";
import { DiscardRecordUseCase } from "~/v1/domain/usecases/discard-record-use-case";
import { SubmitRecordUseCase } from "~/v1/domain/usecases/submit-record-use-case";
import { SaveDraftRecord } from "~/v1/domain/usecases/save-draft-use-case";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";
import { useQueue } from "~/v1/infrastructure/services/useQueue";

export const useQuestionFormViewModel = () => {
  const queue = useQueue();
  const debounceForSubmit = useDebounce(300);

  const isDraftSaving = ref(false);
  const isDiscarding = ref(false);
  const isSubmitting = ref(false);
  const discardUseCase = useResolve(DiscardRecordUseCase);
  const submitUseCase = useResolve(SubmitRecordUseCase);
  const saveDraftUseCase = useResolve(SaveDraftRecord);

  const discard = async (record: Record) => {
    isDiscarding.value = true;

    await queue.enqueue(() => {
      return discardUseCase.execute(record);
    });

    await debounceForSubmit.wait();

    isDiscarding.value = false;
  };

  const submit = async (record: Record) => {
    isSubmitting.value = true;

    await queue.enqueue(() => {
      return submitUseCase.execute(record);
    });

    await debounceForSubmit.wait();

    isSubmitting.value = false;
  };

  const saveAsDraft = async (record: Record) => {
    isDraftSaving.value = true;

    await queue.enqueue(() => {
      return saveDraftUseCase.execute(record);
    });

    await debounceForSubmit.wait();
    isDraftSaving.value = false;
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
