import { computed, onBeforeMount, ref } from "vue-demi";
import {
  useEvents,
  UpdateMetricsEventHandler,
} from "~/v1/infrastructure/events";
import { useRunningEnvironment } from "~/v1/infrastructure/services";
import { useMetrics } from "~/v1/infrastructure/storage/MetricsStorage";

export const useAnnotationProgressViewModel = () => {
  const isShareYourProgressEnabled = ref<boolean>(false);

  const { state: metrics } = useMetrics();
  const { getShareYourProgressEnabled } = useRunningEnvironment();

  onBeforeMount(async () => {
    isShareYourProgressEnabled.value = await getShareYourProgressEnabled();
  });

  const canSeeShare = computed(() => metrics.submitted > 0);
  const shouldShowSubmittedAnimation = computed(
    () => metrics.submitted % 20 === 0
  );

  onBeforeMount(() => {
    useEvents(UpdateMetricsEventHandler);
  });

  return {
    metrics,
    isShareYourProgressEnabled,
    canSeeShare,
    shouldShowSubmittedAnimation,
  };
};
