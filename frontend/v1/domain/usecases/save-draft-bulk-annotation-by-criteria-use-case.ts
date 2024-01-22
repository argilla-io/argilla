import { Record } from "../entities/record/Record";
import { RecordCriteria } from "../entities/record/RecordCriteria";
import { Records } from "../entities/record/Records";
import { GetRecordsByCriteriaUseCase } from "./get-records-by-criteria-use-case";
import { LoadRecordsToAnnotateUseCase } from "./load-records-to-annotate-use-case";
import { SaveDraftBulkAnnotationUseCase } from "./save-draft-bulk-annotation-use-case";

const chunk = <T>(array: T[], size: number) => {
  const chunks: T[][] = [];

  for (let i = 0; i < array.length; i += size) {
    const chunk = array.slice(i, i + size);

    chunks.push(chunk);
  }

  return chunks;
};

type Progress = (value: number) => void;

const RECORDS_TO_AFFECT = 20;
const CHUNK_SIZE = 5;

export class SaveDraftBulkByCriteriaUseCase {
  constructor(
    private readonly getRecords: GetRecordsByCriteriaUseCase,
    private readonly saveDraftBulk: SaveDraftBulkAnnotationUseCase,
    private readonly loadRecords: LoadRecordsToAnnotateUseCase
  ) {}

  async execute(
    criteria: RecordCriteria,
    referenceRecord: Record,
    progress: Progress = () => {}
  ) {
    const results: boolean[] = [];
    const newCriteria = criteria.clone();
    newCriteria.page.goToFirst(RECORDS_TO_AFFECT);

    const records = await this.getRecords.execute(newCriteria);
    debugger;

    const chunks = chunk(records.records, CHUNK_SIZE);

    for (const recordsToProcess of chunks) {
      const allSuccessful = await this.saveDraftBulk.execute(
        recordsToProcess,
        referenceRecord
      );

      results.push(allSuccessful);

      progress(this.getNewProgress(results, records));
    }

    await this.loadRecords.load(criteria);

    return results.every((r) => r);
  }

  private getNewProgress(results: boolean[], records: Records): number {
    return (results.length * CHUNK_SIZE) / records.records.length;
  }
}
