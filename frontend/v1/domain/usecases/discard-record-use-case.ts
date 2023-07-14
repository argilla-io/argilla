import { IEventDispatcher } from "@codescouts/events";
import { RecordResponseUpdated } from "../events/RecordResponseUpdated";
import { Record } from "@/v1/domain/entities/record/Record";
import { RecordRepository } from "@/v1/infrastructure/repositories";

export class DiscardRecordUseCase {
  constructor(
    private readonly recordRepository: RecordRepository,
    private readonly eventDispatcher: IEventDispatcher
  ) {}

  async execute(record: Record) {
    record.discard();

    await this.recordRepository.discardRecordResponse(record);

    this.eventDispatcher.dispatch(new RecordResponseUpdated(record));
  }
}
