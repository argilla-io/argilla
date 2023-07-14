import { Record } from "@/v1/domain/entities/record/Record";
import { RecordRepository } from "@/v1/infrastructure/repositories";

export class DiscardRecordUseCase {
  constructor(private readonly recordRepository: RecordRepository) {}

  async execute(record: Record) {
    record.discard();

    await this.recordRepository.discardRecordResponse(record);
  }
}
