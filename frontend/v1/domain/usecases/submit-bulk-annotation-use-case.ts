import { IEventDispatcher } from "@codescouts/events";
import { Record } from "../entities/record/Record";
import { RecordResponseUpdatedEvent } from "../events/RecordResponseUpdatedEvent";
import { RecordRepository } from "~/v1/infrastructure/repositories";

export class SubmitBulkAnnotationUseCase {
  constructor(
    private readonly recordRepository: RecordRepository,
    private readonly eventDispatcher: IEventDispatcher
  ) {}

  async execute(records: Record[], recordReference: Record) {
    records.forEach((record) => record.answerWith(recordReference));

    const responses = await this.recordRepository.submitBulkRecordResponse(
      records
    );

    responses
      .filter((r) => r.success)
      .forEach(({ recordId, response }) => {
        const record = records.find((r) => r.id === recordId);

        record.submit(response);
      });

    this.eventDispatcher.dispatch(
      new RecordResponseUpdatedEvent(recordReference)
    );

    return responses.every((r) => r.success);
  }
}
