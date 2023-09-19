import { IEventDispatcher } from "@codescouts/events";
import { RecordResponseUpdatedEvent } from "../events/RecordResponseUpdatedEvent";
import { Record } from "@/v1/domain/entities/record/Record";
import { RecordRepository } from "@/v1/infrastructure/repositories";

export class ClearRecordUseCase {
  constructor(
    private readonly recordRepository: RecordRepository,
    private readonly eventDispatcher: IEventDispatcher
  ) {}

  async execute(record: Record) {
    await this.recordRepository.deleteRecordResponse(record);

    if (record.answer) {
      this.eventDispatcher.dispatch(new RecordResponseUpdatedEvent(record));
    }

    record.clear();
  }
}
