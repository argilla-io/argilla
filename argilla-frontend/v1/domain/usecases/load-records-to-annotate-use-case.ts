import { RecordCriteria } from "../entities/record/RecordCriteria";
import { IRecordStorage } from "../services/IRecordStorage";
import { GetRecordsByCriteriaUseCase } from "./get-records-by-criteria-use-case";

export class LoadRecordsToAnnotateUseCase {
  private isBuffering = false;

  constructor(
    private readonly getRecords: GetRecordsByCriteriaUseCase,
    private readonly recordsStorage: IRecordStorage
  ) {}

  async load(criteria: RecordCriteria): Promise<void> {
    const { page } = criteria;

    let newRecords = await this.getRecords.execute(criteria);
    let isRecordExistForCurrentPage = newRecords.existsRecordOn(page);

    if (!isRecordExistForCurrentPage && !page.isFirstPage()) {
      criteria.page.goToFirst();

      newRecords = await this.getRecords.execute(criteria);

      isRecordExistForCurrentPage = newRecords.existsRecordOn(page);
    }

    if (isRecordExistForCurrentPage) {
      const record = newRecords.getRecordOn(page);

      record.initialize();
    }

    criteria.commit();

    this.recordsStorage.save(newRecords);
  }

  async paginate(criteria: RecordCriteria) {
    const { page, isFilteringBySimilarity } = criteria;

    const records = this.recordsStorage.get();
    let isNextRecordExist = records.existsRecordOn(page);

    if (!isFilteringBySimilarity && !isNextRecordExist) {
      const newRecords = await this.getRecords.execute(criteria);

      records.append(newRecords);

      isNextRecordExist = records.existsRecordOn(page);

      this.recordsStorage.save(records);
    }

    if (isNextRecordExist) {
      const record = records.getRecordOn(page);

      record.initialize();

      criteria.commit();
    }

    this.loadBuffer(criteria);

    return isNextRecordExist;
  }

  private loadBuffer(criteria: RecordCriteria) {
    const { page, isFilteringBySimilarity, isPaginatingBackward } = criteria;

    if (isFilteringBySimilarity || isPaginatingBackward) return;

    const records = this.recordsStorage.get();

    if (!records.hasNecessaryBuffering(page)) {
      this.loadBufferedRecords(criteria);
    }
  }

  private async loadBufferedRecords(criteria: RecordCriteria) {
    if (this.isBuffering) return;

    const { isPaginatingForward } = criteria;

    const records = this.recordsStorage.get();
    const newCriteria = criteria.clone();

    try {
      this.isBuffering = true;

      if (isPaginatingForward) {
        newCriteria.page.goTo(records.lastRecord.page + 1);
      }

      const newRecords = await this.getRecords.execute(newCriteria);

      records.append(newRecords);

      this.recordsStorage.save(records);
    } catch {
    } finally {
      this.isBuffering = false;
    }
  }
}
