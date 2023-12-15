import { PageCriteria } from "../page/PageCriteria";
import { Record } from "./Record";
import { RecordStatus } from "./RecordAnswer";
import { RecordCriteria } from "./RecordCriteria";

export class Records {
  public readonly records: Record[];
  constructor(records: Record[] = [], public readonly total: number = 0) {
    this.records = records.sort((r1, r2) => (r1.page < r2.page ? -1 : 1));
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

      if (isMovingForward) {
        const recordsAnnotated = this.quantityOfRecordsAnnotated(status);

        return page.synchronizePagination({
          from: this.lastRecord.page + 1 - recordsAnnotated,
          many: page.client.many,
        });
      } else if (this.firstRecord.page > page.client.page)
        return page.synchronizePagination({
          from: this.firstRecord.page - 1,
          many: 1,
        });
    }

    page.synchronizePagination({
      from: page.client.page,
      many: page.client.many,
    });
  }

  private get lastRecord() {
    return this.records[this.records.length - 1];
  }

  private get firstRecord() {
    return this.records[0];
  }

  private quantityOfRecordsAnnotated(status: RecordStatus) {
    if (status === "pending")
      return this.records.filter(
        (record) => record.status !== "draft" && record.status !== status
      ).length;

    return this.records.filter((record) => record.status !== status).length;
  }
}

export class RecordsWithReference extends Records {
  constructor(records: Record[], total, public readonly reference: Record) {
    super(records, total);
  }
}
