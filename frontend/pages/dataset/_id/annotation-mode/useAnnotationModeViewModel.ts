import { onBeforeMount } from "vue-demi";
import { useDatasetSettingViewModel } from "../useDatasetSettingViewModel";
import {
  UpdateMetricsEventHandler,
  useEvents,
} from "~/v1/infrastructure/events";

export const useAnnotationModeViewModel = () => {
  const viewModel = useDatasetSettingViewModel();

  onBeforeMount(() => {
    useEvents(() => {
      new UpdateMetricsEventHandler();
    });
  });

  return { ...viewModel };
};
