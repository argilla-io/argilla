import { IEventDispatcher } from "@codescouts/events";
import { Record } from "../entities/record/Record";
import { RecordResponseUpdatedEvent } from "../events/RecordResponseUpdatedEvent";
import { RecordRepository } from "@/v1/infrastructure/repositories";

export class SubmitRecordUseCase {
  constructor(
    private readonly recordRepository: RecordRepository,
    private readonly eventDispatcher: IEventDispatcher
  ) {}

  async execute(record: Record) {
    const response = await this.recordRepository.submitRecordResponse(record);

    record.submit(response);

    this.eventDispatcher.dispatch(new RecordResponseUpdatedEvent(record));
  }
}
