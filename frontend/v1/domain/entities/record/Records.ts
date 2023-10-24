import { Pagination } from "../Pagination";
import { Record } from "./Record";
import { RecordCriteria } from "./RecordCriteria";

const NEXT_RECORDS_TO_FETCH = 10;

export class Records {
  public readonly records: Record[];
  constructor(records: Record[] = [], public readonly total: number = 0) {
    this.records = records.sort((r1, r2) => (r1.page < r2.page ? -1 : 1));
  }

  get hasRecordsToAnnotate() {
    return this.records.length > 0;
  }

  existsRecordOn(page: number) {
    return !!this.getRecordOn(page);
  }

  getRecordOn(page: number) {
    return this.records.find((record) => record.page === page);
  }

  getPageToFind(criteria: RecordCriteria): Pagination {
    const { page, status, isFilteringBySimilarity, similaritySearch } =
      criteria;

    if (isFilteringBySimilarity)
      return { from: 1, many: similaritySearch.limit };

    const currentPage: Pagination = {
      from: page,
      many: NEXT_RECORDS_TO_FETCH,
    };

    if (!this.hasRecordsToAnnotate) return currentPage;

    const recordsAnnotated = this.quantityOfRecordsAnnotated(status);
    const isMovingToNext = page > this.lastRecord.page;

    if (isMovingToNext) {
      return {
        from: this.lastRecord.page + 1 - recordsAnnotated,
        many: NEXT_RECORDS_TO_FETCH,
      };
    } else if (this.firstRecord.page > page)
      return {
        from: this.firstRecord.page - 1,
        many: 1,
      };

    return currentPage;
  }

  private get lastRecord() {
    return this.records[this.records.length - 1];
  }

  private get firstRecord() {
    return this.records[0];
  }

  private quantityOfRecordsAnnotated(status: string) {
    return this.records.filter((record) => record.status !== status).length;
  }
}
