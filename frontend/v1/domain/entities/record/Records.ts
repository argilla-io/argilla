import { Record } from "./Record";

export class Records {
  constructor(
    public readonly records: Record[] = [],
    public readonly total: number = 0
  ) {}

  get hasRecordsToAnnotate() {
    return this.records.length;
  }

  existsRecordOn(page: number) {
    return !!this.getRecordOn(page);
  }

  getRecordOn(page: number) {
    const arrayOffset = page - 1;
    return this.records.find((record) => record.arrayOffset === arrayOffset);
  }

  getOffsetToFind(page: number, status: string): number {
    if (this.records.length < page - 1) return page - 1;
    const previousRecords = this.records.slice(0, page);

    return previousRecords.filter((record) => record.status === status).length;
  }
}
