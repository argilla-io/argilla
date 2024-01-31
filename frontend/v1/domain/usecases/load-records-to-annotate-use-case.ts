import { RecordCriteria } from "../entities/record/RecordCriteria";
import { IRecordStorage } from "../services/IRecordStorage";
import { GetRecordsByCriteriaUseCase } from "./get-records-by-criteria-use-case";

export class LoadRecordsToAnnotateUseCase {
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

  async paginate(criteria: RecordCriteria): Promise<boolean> {
    const { page } = criteria;
    const records = this.recordsStorage.get();
    let isNextRecordExist = records.existsRecordOn(page);

    if (!criteria.isFilteringBySimilarity) {
      if (!isNextRecordExist) {
        const newRecords = await this.getRecords.execute(criteria);

        records.append(newRecords);

        isNextRecordExist = records.existsRecordOn(page);
      }
    }

    if (isNextRecordExist) {
      const record = records.getRecordOn(page);

      record.initialize();

      criteria.commit();
    }

    this.recordsStorage.save(records);

    return isNextRecordExist;
  }
}
