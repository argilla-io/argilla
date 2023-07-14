import { Record } from "@/v1/domain/entities/record/Record";
import { RecordRepository } from "@/v1/infrastructure/repositories";

export class ClearRecordUseCase {
  constructor(private readonly recordRepository: RecordRepository) {}

  async execute(record: Record) {
    if (record.answer) {
      await this.recordRepository.deleteRecordResponse(record.answer);
    }

    record.clear();
  }
}
