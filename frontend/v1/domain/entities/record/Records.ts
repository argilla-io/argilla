import { Record } from "./Record";

export class Records {
  constructor(
    public readonly records: Record[] = [],
    public readonly total: number = 0
  ) {}

  get hasRecordsToAnnotate() {
    return this.records.length;
  }

  exists(datasetId: string, page: number) {
    const records = this.records.filter(
      (record) => record.datasetId === datasetId
    );

    return !!records[page];
  }
}
