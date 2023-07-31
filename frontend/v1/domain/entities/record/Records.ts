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
}
