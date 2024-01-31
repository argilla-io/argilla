import { PageCriteria } from "../page/PageCriteria";
import { Record } from "./Record";
import { RecordStatus } from "./RecordAnswer";
import { RecordCriteria } from "./RecordCriteria";

export class Records {
  constructor(
    public records: Record[] = [],
    public readonly total: number = 0
  ) {
    this.arrangeQueue();
  }

  get hasRecordsToAnnotate() {
    return this.records.length > 0;
  }

  existsRecordOn(criteria: PageCriteria) {
    return !!this.getRecordOn(criteria);
  }

  getRecordOn(criteria: PageCriteria) {
    return this.records.find((record) => record.page === criteria.client.page);
  }

  getRecordsOn(criteria: PageCriteria): Record[] {
    return this.records
      .filter((record) => record.page >= criteria.client.page)
      .splice(0, criteria.client.many);
  }

  getById(recordId: string): Record {
    return this.records.find((record) => record.id === recordId);
  }

  synchronizeQueuePagination(criteria: RecordCriteria): void {
    const {
      page,
      status,
      isFilteringBySimilarity,
      similaritySearch,
      committed,
    } = criteria;

    if (page.isBulkMode && committed.page.isFocusMode) return;
    if (page.isFocusMode && committed.page.isBulkMode) return;

    if (isFilteringBySimilarity) {
      return page.synchronizePagination({
        from: 1,
        many: similaritySearch.limit,
      });
    }

    if (this.hasRecordsToAnnotate) {
      const isMovingForward = page.client.page > this.lastRecord.page;

      const recordsAnnotated = this.recordsAnnotatedOnQueue(status);

      if (isMovingForward) {
        return page.synchronizePagination({
          from: this.lastRecord.page + 1 - recordsAnnotated,
          many: page.client.many,
        });
      }

      const isMovingBackward = this.firstRecord.page > page.client.page;

      if (isMovingBackward) {
        if (page.isBulkMode)
          return page.synchronizePagination({
            from: this.firstRecord.page - page.client.many,
            many: page.client.many,
          });

        return page.synchronizePagination({
          from: this.firstRecord.page - 1,
          many: 1,
        });
      }
    }

    page.synchronizePagination({
      from: page.client.page,
      many: page.client.many,
    });
  }

  append(newRecords: Records) {
    newRecords.records.forEach((newRecord) => {
      const recordIndex = this.records.findIndex(
        (record) => record.id === newRecord.id
      );

      if (recordIndex === -1) {
        this.records.push(newRecord);
      } else {
        this.records[recordIndex] = newRecord;
      }
    });

    this.arrangeQueue();
  }

  private arrangeQueue() {
    this.records = this.records.sort((r1, r2) => (r1.page < r2.page ? -1 : 1));
  }

  private get lastRecord() {
    return this.records[this.records.length - 1];
  }

  private get firstRecord() {
    return this.records[0];
  }

  private recordsAnnotatedOnQueue(status: RecordStatus) {
    return this.records.filter((record) => record.status !== status).length;
  }
}

export class RecordsWithReference extends Records {
  constructor(records: Record[], total, public readonly reference: Record) {
    super(records, total);
  }
}
