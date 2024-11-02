import { RecordCriteria } from "../entities/record/RecordCriteria";
import { IRecordStorage } from "../services/IRecordStorage";
import { GetDatasetProgressUseCase } from "./get-dataset-progress-use-case";
import { GetRecordsByCriteriaUseCase } from "./get-records-by-criteria-use-case";
import { GetUserMetricsUseCase } from "./get-user-metrics-use-case";

export class LoadRecordsToAnnotateUseCase {
  private isBuffering = false;

  constructor(
    private readonly getRecords: GetRecordsByCriteriaUseCase,
    private readonly getProgress: GetDatasetProgressUseCase,
    private readonly getMetrics: GetUserMetricsUseCase,
    private readonly recordsStorage: IRecordStorage
  ) {}

  async load(criteria: RecordCriteria) {
    const { page } = criteria;

    let [newRecords] = await Promise.all([
      this.getRecords.execute(criteria),
      this.getProgress.execute(criteria.datasetId),
      this.getMetrics.execute(criteria.datasetId),
    ]);

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

    return newRecords;
  }

  async paginate(criteria: RecordCriteria) {
    const { page, isFilteringBySimilarity } = criteria;

    const records = this.recordsStorage.get();
    let isNextRecordExist = records.existsRecordOn(page);

    if (!isFilteringBySimilarity && !isNextRecordExist) {
      const newRecords = await this.getRecords.execute(criteria);

      if (newRecords.hasRecordsToAnnotate) records.append(newRecords);

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

    if (records.shouldBuffering(page)) {
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

      if (newRecords.hasRecordsToAnnotate) records.append(newRecords);

      this.recordsStorage.save(records);
    } catch {
    } finally {
      this.isBuffering = false;
    }
  }
}
