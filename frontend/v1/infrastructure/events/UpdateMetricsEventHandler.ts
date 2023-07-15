import { Handler } from "@codescouts/events";
import { useResolve } from "ts-injecty";
import { RecordResponseUpdated } from "@/v1/domain/events/RecordResponseUpdated";
import { GetUserMetricsUseCase } from "@/v1/domain/usecases/get-user-metrics-use-case";

export class UpdateMetricsEventHandler extends Handler<RecordResponseUpdated> {
  constructor() {
    super(RecordResponseUpdated);
  }

  protected handle(event: RecordResponseUpdated): void | Promise<any> {
    const getUserMetrics = useResolve(GetUserMetricsUseCase);

    getUserMetrics.execute(event.record.datasetId);
  }
}
