import { onBeforeMount } from "vue-demi";
import {
  useEvents,
  UpdateMetricsEventHandler,
} from "~/v1/infrastructure/events";
import { useMetrics } from "~/v1/infrastructure/storage/MetricsStorage";

export const useAnnotationProgressViewModel = () => {
  const { state: metrics } = useMetrics();

  onBeforeMount(() => {
    useEvents(UpdateMetricsEventHandler);
  });

  return {
    metrics,
  };
};
