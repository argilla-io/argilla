import { useResolve } from "ts-injecty";
import { onBeforeMount } from "vue-demi";
import { GetUserMetricsUseCase } from "~/v1/domain/usecases/get-user-metrics-use-case";
import {
  useEvents,
  UpdateMetricsEventHandler,
} from "~/v1/infrastructure/events";
import { useMetrics } from "~/v1/infrastructure/storage/MetricsStorage";

interface FeedbackTaskProgressProps {
  datasetId: string;
}

export const useFeedbackTaskProgressViewModel = (
  props: FeedbackTaskProgressProps
) => {
  const { state: datasetMetrics } = useMetrics();
  const getMetrics = useResolve(GetUserMetricsUseCase);

  const loadMetrics = (datasetId: string) => {
    getMetrics.execute(datasetId);
  };

  onBeforeMount(() => {
    useEvents(() => {
      new UpdateMetricsEventHandler();
    });

    loadMetrics(props.datasetId);
  });

  return {
    datasetMetrics,
  };
};
