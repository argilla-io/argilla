import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Record } from "~/v1/domain/entities/record/Record";
import { ClearRecordUseCase } from "~/v1/domain/usecases/clear-record-use-case";
import { DiscardRecordUseCase } from "~/v1/domain/usecases/discard-record-use-case";
import {
  SaveDraftRecord,
  SubmitRecordUseCase,
} from "~/v1/domain/usecases/submit-record-use-case";

export const useQuestionFormViewModel = () => {
  const discardUseCase = useResolve(DiscardRecordUseCase);
  const submitUseCase = useResolve(SubmitRecordUseCase);
  const clearUseCase = useResolve(ClearRecordUseCase);

  const discard = async (record: Record) => {
    await discardUseCase.execute(record);
  };

  const submit = async (record: Record) => {
    await submitUseCase.execute(record);
  };

  const clear = async (record: Record) => {
    await clearUseCase.execute(record);
  };

  const savingDraft = ref("PENDING");

  const saveDraftUseCase = useResolve(SaveDraftRecord);

  const saveDraft = async (record: Record) => {
    savingDraft.value = "SAVING";

    try {
      await saveDraftUseCase.execute(record);

      savingDraft.value = "SAVED";
    } catch {
      savingDraft.value = "ERROR";
    }
  };

  return { clear, submit, discard, savingDraft, saveDraft };
};
