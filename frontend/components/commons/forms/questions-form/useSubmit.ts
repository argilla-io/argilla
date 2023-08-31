import { useResolve } from "ts-injecty";
import { computed, Ref } from "vue-demi";
import { SubmitRecordUseCase } from "~/v1/domain/usecases/submit-record-use-case";
import { Debounce } from "~/v1/infrastructure/services/useDebounce";
import { Queue } from "~/v1/infrastructure/services/useQueue";
import { Record } from "~/v1/domain/entities/record/Record";

export const useSubmit = (
  record: Record,
  questionAreCompletedCorrectly: Ref<boolean>,
  isFormTouched: Ref<boolean>,
  debounce: Debounce,
  queue: Queue,
  { emit }
) => {
  const submitUseCase = useResolve(SubmitRecordUseCase);

  const isSubmitButtonDisabled = computed((): boolean => {
    if (record.isSubmitted)
      return !isFormTouched.value || !questionAreCompletedCorrectly.value;

    return !questionAreCompletedCorrectly.value;
  });

  const submit = (record: Record) => {
    debounce.stop();

    queue.enqueue(() => {
      return submitUseCase.execute(record);
    });
  };

  const onSubmit = async () => {
    if (!questionAreCompletedCorrectly) return;

    await submit(record);

    emit("on-submit-responses");
  };

  return { isSubmitButtonDisabled, onSubmit };
};
