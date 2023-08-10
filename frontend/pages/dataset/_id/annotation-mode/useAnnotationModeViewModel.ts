import { getCurrentInstance, onBeforeMount } from "vue-demi";
import { useResolve } from "ts-injecty";
import { useDatasetViewModel } from "../useDatasetViewModel";
import {
  UpdateMetricsEventHandler,
  useEvents,
} from "@/v1/infrastructure/events";
import { SaveDraftRecord } from "~/v1/domain/usecases/save-draft-use-case";
import { Record } from "~/v1/domain/entities/record/Record";

export const useAnnotationModeViewModel = () => {
  const datasetViewModel = useDatasetViewModel();
  const saveDraftUseCase = useResolve(SaveDraftRecord);
  const instance = getCurrentInstance();

  onBeforeMount(() => {
    useEvents(() => {
      new UpdateMetricsEventHandler();
    });

    datasetViewModel.loadDataset();
  });

  const onSaveDraft = async (record: Record) => {
    if (!record.hasAnyQuestionAnswered) return;

    instance.proxy.$root.$emit("record-saving", true);

    try {
      await saveDraftUseCase.execute(record);
    } catch {
    } finally {
      instance.proxy.$root.$emit("record-saving", false);
    }
  };

  let timer = null;
  const saveDraft = (record: Record) => {
    if (timer) clearTimeout(timer);

    timer = setTimeout(() => {
      onSaveDraft(record);
    }, 2000);
  };

  return { ...datasetViewModel, saveDraft };
};
