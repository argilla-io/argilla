import { IEventDispatcher } from "@codescouts/events";
import { RecordResponseUpdatedEvent } from "../events/RecordResponseUpdatedEvent";
import { Record } from "../entities/record/Record";
import { RecordRepository } from "@/v1/infrastructure/repositories";

export class SaveDraftRecord {
  constructor(
    private readonly recordRepository: RecordRepository,
    private readonly eventDispatcher: IEventDispatcher
  ) {}

  async execute(record: Record) {
    const response = await this.recordRepository.saveDraft(record);

    if (record.answer) {
      this.eventDispatcher.dispatch(new RecordResponseUpdatedEvent(record));
    }
    record.submit(response);
  }
}
