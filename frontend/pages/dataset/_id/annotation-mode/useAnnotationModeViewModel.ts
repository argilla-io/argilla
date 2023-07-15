import { onBeforeMount } from "vue-demi";
import { useDatasetViewModel } from "../useDatasetViewModel";
import {
  UpdateMetricsEventHandler,
  useEvents,
} from "@/v1/infrastructure/events";

export const useAnnotationModeViewModel = () => {
  const datasetViewModel = useDatasetViewModel();

  onBeforeMount(() => {
    useEvents(() => {
      new UpdateMetricsEventHandler();
    });

    datasetViewModel.loadDataset();
  });

  return { ...datasetViewModel };
};
