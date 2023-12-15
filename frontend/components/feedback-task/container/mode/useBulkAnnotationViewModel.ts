import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Record } from "~/v1/domain/entities/record/Record";
import { DiscardBulkAnnotationUseCase } from "~/v1/domain/usecases/discard-bulk-annotation-use-case";
import { SubmitBulkAnnotationUseCase } from "~/v1/domain/usecases/submit-bulk-annotation-use-case";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";
import { useQueue } from "~/v1/infrastructure/services/useQueue";

export const useBulkAnnotationViewModel = () => {
  const queue = useQueue();
  const debounceForSubmit = useDebounce(300);

  const isDraftSaving = ref(false);
  const isDiscarding = ref(false);
  const isSubmitting = ref(false);
  const discardUseCase = useResolve(DiscardBulkAnnotationUseCase);
  const submitUseCase = useResolve(SubmitBulkAnnotationUseCase);

  const discard = async (records: Record[], recordReference: Record) => {
    isDiscarding.value = true;

    await queue.enqueue(() => {
      return discardUseCase.execute(records, recordReference);
    });

    await debounceForSubmit.wait();

    isDiscarding.value = false;
  };

  const submit = async (records: Record[], recordReference: Record) => {
    isSubmitting.value = true;

    await queue.enqueue(() => {
      return submitUseCase.execute(records, recordReference);
    });

    await debounceForSubmit.wait();

    isSubmitting.value = false;
  };

  return {
    isDraftSaving,
    isDiscarding,
    isSubmitting,
    submit,
    discard,
  };
};
