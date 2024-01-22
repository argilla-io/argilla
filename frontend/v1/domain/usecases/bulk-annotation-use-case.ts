import { IEventDispatcher } from "@codescouts/events";
import { Record } from "../entities/record/Record";
import { RecordResponseUpdatedEvent } from "../events/RecordResponseUpdatedEvent";
import { RecordCriteria } from "../entities/record/RecordCriteria";
import { RecordStatus } from "../entities/record/RecordAnswer";
import { GetRecordsByCriteriaUseCase } from "./get-records-by-criteria-use-case";
import { LoadRecordsToAnnotateUseCase } from "./load-records-to-annotate-use-case";
import { RecordRepository } from "~/v1/infrastructure/repositories";

export type AvailableStatus = Exclude<RecordStatus, "pending">;

type Progress = (value: number) => void;

const RECORDS_TO_AFFECT = 20;
const CHUNK_SIZE = 5;

export class BulkAnnotationUseCase {
  constructor(
    private readonly getRecords: GetRecordsByCriteriaUseCase,
    private readonly loadRecords: LoadRecordsToAnnotateUseCase,
    private readonly recordRepository: RecordRepository,
    private readonly eventDispatcher: IEventDispatcher
  ) {}

  async execute(
    status: AvailableStatus,
    criteria: RecordCriteria,
    recordReference: Record,
    selectedRecords: Record[],
    affectAllRecords = false,
    progress: Progress = () => {}
  ) {
    const results: boolean[] = [];
    const records = [...selectedRecords];

    if (affectAllRecords) {
      const newCriteria = criteria.clone();
      newCriteria.page.goToFirst(RECORDS_TO_AFFECT);

      const allRecords = await this.getRecords.execute(newCriteria);

      records.push(...allRecords.records);
    }

    const chunks = this.chunk(records, CHUNK_SIZE);

    for (const recordsToAnnotate of chunks) {
      const allSuccessful = await this.save(
        status,
        recordsToAnnotate,
        recordReference
      );

      results.push(allSuccessful);

      progress(this.calculateProgress(results, records));
    }

    if (affectAllRecords) {
      await this.loadRecords.load(criteria);
    }

    return results.every((r) => r);
  }

  private async save(
    status: AvailableStatus,
    records: Record[],
    recordReference: Record
  ) {
    records.forEach((record) => record.answerWith(recordReference));

    const responses = await this.recordRepository.annotateBulkRecords(
      records,
      status
    );

    responses
      .filter((r) => r.success)
      .forEach(({ recordId, response }) => {
        const record = records.find((r) => r.id === recordId);

        record.submit(response);
      });

    this.eventDispatcher.dispatch(
      new RecordResponseUpdatedEvent(recordReference)
    );

    return responses.every((r) => r.success);
  }

  private chunk<T>(array: T[], size: number) {
    const chunks: T[][] = [];

    for (let i = 0; i < array.length; i += size) {
      const chunk = array.slice(i, i + size);

      chunks.push(chunk);
    }

    return chunks;
  }

  private calculateProgress(results: boolean[], records: Record[]): number {
    const value = (results.length * CHUNK_SIZE) / records.length;

    return Math.trunc(value * 100);
  }
}
