import { useResolve } from "ts-injecty";
import { Ref, computed } from "vue-demi";
import { SubmitRecordUseCase } from "~/v1/domain/usecases/submit-record-use-case";
import { Debounce } from "~/v1/infrastructure/services/useDebounce";
import { Record } from "~/v1/domain/entities/record/Record";
import { Queue } from "~/v1/infrastructure/services/useQueue";
import { TBeforeUnload } from "~/v1/infrastructure/services/useBeforeUnload";

export const useSubmit = (
  record: Record,
  beforeUnload: TBeforeUnload,
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

  const onSubmit = async () => {
    if (isSubmitButtonDisabled.value) return;
    beforeUnload.destroy();

    await submit(record);

    emit("on-submit-responses");
  };

  const submit = (record: Record) => {
    debounce.stop();

    queue.enqueue(() => {
      return submitUseCase.execute(record);
    });
  };

  return { isSubmitButtonDisabled, onSubmit };
};
