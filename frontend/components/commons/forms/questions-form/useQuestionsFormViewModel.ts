import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Record } from "~/v1/domain/entities/record/Record";
import { ClearRecordUseCase } from "~/v1/domain/usecases/clear-record-use-case";
import { DiscardRecordUseCase } from "~/v1/domain/usecases/discard-record-use-case";
import { SubmitRecordUseCase } from "~/v1/domain/usecases/submit-record-use-case";
import { SaveDraftRecord } from "~/v1/domain/usecases/save-draft-use-case";

export const useQuestionFormViewModel = () => {
  const discardUseCase = useResolve(DiscardRecordUseCase);
  const submitUseCase = useResolve(SubmitRecordUseCase);
  const clearUseCase = useResolve(ClearRecordUseCase);
  const saveDraftUseCase = useResolve(SaveDraftRecord);

  const discard = async (record: Record) => {
    await discardUseCase.execute(record);
  };

  const submit = async (record: Record) => {
    await submitUseCase.execute(record);
  };

  const clear = async (record: Record) => {
    await clearUseCase.execute(record);
  };

  const draftSaving = ref(false);
  const onSaveDraft = async (record: Record) => {
    if (!record.hasAnyQuestionAnswered) return;
    draftSaving.value = true;
    try {
      await saveDraftUseCase.execute(record);
    } catch {
    } finally {
      draftSaving.value = false;
    }
  };

  let timer = null;
  const saveDraft = (record: Record) => {
    if (timer) clearTimeout(timer);

    timer = setTimeout(() => {
      onSaveDraft(record);
    }, 2000);
  };

  return { clear, submit, discard, saveDraft, draftSaving };
};
