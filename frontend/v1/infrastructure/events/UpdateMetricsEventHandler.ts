import { Handler } from "@codescouts/events";
import { useResolve } from "ts-injecty";
import { RecordResponseUpdatedEvent } from "~/v1/domain/events/RecordResponseUpdatedEvent";
import { GetUserMetricsUseCase } from "@/v1/domain/usecases/get-user-metrics-use-case";

export class UpdateMetricsEventHandler extends Handler<RecordResponseUpdatedEvent> {
  constructor() {
    super(RecordResponseUpdatedEvent);
  }

  protected handle(event: RecordResponseUpdatedEvent): void | Promise<any> {
    const getUserMetrics = useResolve(GetUserMetricsUseCase);

    getUserMetrics.execute(event.record.datasetId);
  }
}
