import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Record } from "~/v1/domain/entities/record/Record";
import { DiscardBulkAnnotationUseCase } from "~/v1/domain/usecases/discard-bulk-annotation-use-case";
import { SaveDraftBulkAnnotationUseCase } from "~/v1/domain/usecases/save-draft-bulk-annotation-use-case";
import { SubmitBulkAnnotationUseCase } from "~/v1/domain/usecases/submit-bulk-annotation-use-case";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";

export const useBulkAnnotationViewModel = () => {
  const debounceForSubmit = useDebounce(300);

  const isDraftSaving = ref(false);
  const isDiscarding = ref(false);
  const isSubmitting = ref(false);
  const discardUseCase = useResolve(DiscardBulkAnnotationUseCase);
  const submitUseCase = useResolve(SubmitBulkAnnotationUseCase);
  const saveDraftUseCase = useResolve(SaveDraftBulkAnnotationUseCase);

  const discard = async (records: Record[], recordReference: Record) => {
    isDiscarding.value = true;

    discardUseCase.execute(records, recordReference);

    await debounceForSubmit.wait();

    isDiscarding.value = false;
  };

  const submit = async (records: Record[], recordReference: Record) => {
    isSubmitting.value = true;

    submitUseCase.execute(records, recordReference);

    await debounceForSubmit.wait();

    isSubmitting.value = false;
  };

  const saveAsDraft = async (records: Record[], recordReference: Record) => {
    isDraftSaving.value = true;

    saveDraftUseCase.execute(records, recordReference);

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
