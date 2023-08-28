import { Record } from "./Record";

export class Records {
  public readonly records: Record[];
  constructor(records: Record[] = [], public readonly total: number = 0) {
    this.records = records.sort((r1, r2) => (r1.page < r2.page ? -1 : 1));
  }

  get hasRecordsToAnnotate() {
    return this.records.length;
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
  ): { pageToFind: number; recordsToFetch: number } {
    if (!this.hasRecordsToAnnotate)
      return { pageToFind: page, recordsToFetch: 10 };

    const changedRecords = this.records.filter(
      (record) => record.status !== status
    ).length;

    const firstRecord = this.records[0];
    const latestRecord = this.records[this.records.length - 1];

    const isMovingToNext = page > latestRecord?.page;

    if (isMovingToNext) {
      return {
        pageToFind: latestRecord.page + 1 - changedRecords,
        recordsToFetch: 10,
      };
    } else if (firstRecord.page > page)
      return {
        pageToFind: firstRecord.page - 1,
        recordsToFetch: 1,
      };

    return { pageToFind: page, recordsToFetch: 10 };
  }
}
