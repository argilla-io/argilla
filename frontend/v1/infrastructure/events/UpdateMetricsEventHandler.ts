import { Handler } from "@codescouts/events";
import { useResolve } from "ts-injecty";
import { RecordResponseUpdated } from "@/v1/domain/events/RecordResponseUpdated";
import { GetUserMetricsUseCase } from "@/v1/domain/usecases/get-user-metrics-use-case";

export class UpdateMetricsEventHandler extends Handler<RecordResponseUpdated> {
  private readonly getUserMetrics: GetUserMetricsUseCase;
  constructor() {
    super(RecordResponseUpdated);

    this.getUserMetrics = useResolve(GetUserMetricsUseCase);
  }

  protected handle(event: RecordResponseUpdated): void | Promise<any> {
    this.getUserMetrics.execute(event.record.datasetId);
  }
}
