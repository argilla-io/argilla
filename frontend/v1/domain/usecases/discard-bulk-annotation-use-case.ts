import { IEventDispatcher } from "@codescouts/events";
import { Record } from "../entities/record/Record";
import { RecordResponseUpdatedEvent } from "../events/RecordResponseUpdatedEvent";
import { RecordRepository } from "~/v1/infrastructure/repositories";

export class DiscardBulkAnnotationUseCase {
  constructor(
    private readonly recordRepository: RecordRepository,
    private readonly eventDispatcher: IEventDispatcher
  ) {}

  async execute(records: Record[], recordReference: Record): Promise<void> {
    for (const record of records) {
      try {
        record.answerWith(recordReference);

        const answerDiscarded =
          await this.recordRepository.discardRecordResponse(record);

        record.discard(answerDiscarded);
      } catch (error) {
        // TODO: Handle error
      }
    }

    this.eventDispatcher.dispatch(
      new RecordResponseUpdatedEvent(recordReference)
    );
  }
}
