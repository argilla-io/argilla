import { computed, onBeforeMount } from "vue-demi";
import {
  useEvents,
  UpdateMetricsEventHandler,
} from "~/v1/infrastructure/events";
import { useMetrics } from "~/v1/infrastructure/storage/MetricsStorage";

export const useAnnotationProgressViewModel = () => {
  const { state: metrics } = useMetrics();
  const canSeeShare = computed(() => metrics.submitted > 0);
  const shouldShowSubmittedAnimation = computed(
    () => metrics.submitted % 20 === 0
  );

  onBeforeMount(() => {
    useEvents(UpdateMetricsEventHandler);
  });

  return {
    metrics,
    canSeeShare,
    shouldShowSubmittedAnimation,
  };
};
