import { onBeforeMount } from "vue-demi";
import {
  UpdateMetricsEventHandler,
  useEvents,
} from "~/v1/infrastructure/events";

export const useAnnotationModeViewModel = () => {
  onBeforeMount(() => {
    useEvents(() => {
      new UpdateMetricsEventHandler();
    });
  });
};
