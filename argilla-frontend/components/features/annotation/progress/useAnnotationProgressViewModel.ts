import { useResolve } from "ts-injecty";
import { onBeforeMount } from "vue-demi";
import { GetUserMetricsUseCase } from "~/v1/domain/usecases/get-user-metrics-use-case";
import {
  useEvents,
  UpdateMetricsEventHandler,
} from "~/v1/infrastructure/events";
import { useMetrics } from "~/v1/infrastructure/storage/MetricsStorage";

interface AnnotationProgressProps {
  datasetId: string;
}
export const useAnnotationProgressViewModel = (
  props: AnnotationProgressProps
) => {
  const { state: metrics } = useMetrics();
  const getMetrics = useResolve(GetUserMetricsUseCase);

  onBeforeMount(() => {
    useEvents(UpdateMetricsEventHandler);

    getMetrics.execute(props.datasetId);
  });

  return {
    metrics,
  };
};
