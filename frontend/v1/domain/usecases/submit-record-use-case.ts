import { IEventDispatcher } from "@codescouts/events";
import { Record } from "../entities/record/Record";
import { RecordResponseUpdated } from "../events/RecordResponseUpdated";
import { RecordRepository } from "@/v1/infrastructure/repositories";

export class SubmitRecordUseCase {
  constructor(
    private readonly recordRepository: RecordRepository,
    private readonly eventDispatcher: IEventDispatcher
  ) {}

  async execute(record: Record) {
    const response = await this.recordRepository.submitNewRecordResponse(
      record
    );

    record.submit(response);

    this.eventDispatcher.dispatch(new RecordResponseUpdated(record));
  }
}
