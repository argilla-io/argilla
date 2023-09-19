import { useStoreFor } from "@/v1/store/create";
import { IMetricsStorage } from "@/v1/domain/services/IMetricsStorage";
import { Metrics } from "@/v1/domain/entities/Metrics";

const useStoreForMetrics = useStoreFor<Metrics, IMetricsStorage>(Metrics);
export const useMetrics = () => useStoreForMetrics();
