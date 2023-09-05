import { Record } from "./Record";

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

  getPageToFind(
    page: number,
    status: string
  ): { fromRecord: number; howMany: number } {
    const currentPage = {
      fromRecord: page,
      howMany: NEXT_RECORDS_TO_FETCH,
    };
    if (!this.hasRecordsToAnnotate) return currentPage;
    const recordsAnnotated = this.quantityOfRecordsAnnotated(status);
    const isMovingToNext = page > this.lastRecord.page;

    if (isMovingToNext) {
      return {
        fromRecord: this.lastRecord.page + 1 - recordsAnnotated,
        howMany: NEXT_RECORDS_TO_FETCH,
      };
    } else if (this.firstRecord.page > page)
      return {
        fromRecord: this.firstRecord.page - 1,
        howMany: 1,
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
