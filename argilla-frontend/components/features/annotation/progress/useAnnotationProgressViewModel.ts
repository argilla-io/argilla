import { computed, onBeforeMount } from "vue-demi";
import {
  useEvents,
  UpdateMetricsEventHandler,
} from "~/v1/infrastructure/events";
import { useMetrics } from "~/v1/infrastructure/storage/MetricsStorage";

export const useAnnotationProgressViewModel = () => {
  const { state: metrics } = useMetrics();

  const canSeeShare = computed(() => metrics.submitted >= 2);
  const shouldShowSubmittedAnimation = computed(
    () => canSeeShare.value && metrics.submitted % 10 === 0
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
