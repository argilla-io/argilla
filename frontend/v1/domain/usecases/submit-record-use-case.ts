import { Record } from "../entities/record/Record";
import { RecordAnswer } from "../entities/record/RecordAnswer";
import { RecordRepository } from "@/v1/infrastructure/repositories";

export class SubmitRecordUseCase {
  constructor(private readonly recordRepository: RecordRepository) {}

  async execute(record: Record) {
    const response = await this.recordRepository.submitNewRecordResponse(
      record
    );

    record.submit(
      new RecordAnswer(response.id, response.status, response.values)
    );
  }
}
