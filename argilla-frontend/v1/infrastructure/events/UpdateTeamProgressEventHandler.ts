import { Handler } from "@codescouts/events";
import { useResolve } from "ts-injecty";
import { RecordResponseUpdatedEvent } from "~/v1/domain/events/RecordResponseUpdatedEvent";
import { GetDatasetProgressUseCase } from "~/v1/domain/usecases/get-dataset-progress-use-case";

export class UpdateTeamProgressEventHandler extends Handler<RecordResponseUpdatedEvent> {
  constructor() {
    super(RecordResponseUpdatedEvent);
  }

  protected handle(event: RecordResponseUpdatedEvent): void | Promise<any> {
    const getDatasetProgress = useResolve(GetDatasetProgressUseCase);

    getDatasetProgress.execute(event.record.datasetId);
  }
}
