import { Record } from "../entities/record/Record";
import { RecordRepository } from "@/v1/infrastructure/repositories";

export class SaveDraftRecord {
  constructor(private readonly recordRepository: RecordRepository) {}

  async execute(record: Record) {
    const response = await this.recordRepository.saveDraft(record);

    record.submit(response);
  }
}
