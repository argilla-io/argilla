import { RecordStatus } from "./RecordAnswer";

interface PreviousRecordCriteria {
  page: number;
  status: RecordStatus;
  searchText: string;
  metadata: string[];
  sortBy: string[];
}

export class RecordCriteria {
  public committed: PreviousRecordCriteria;
  public page: number;
  public status: RecordStatus;

  constructor(
    public readonly datasetId: string,
    page: number,
    status: RecordStatus,
    public searchText: string,
    public metadata: string[] = [],
    public sortBy: string[] = []
  ) {
    this.page = page ? Number(page) : 1;
    this.status = status || "pending";
    this.searchText = searchText ?? "";

    this.commit();
  }

  get isFilteringByText() {
    return this.committed.searchText.length > 0;
  }

  get isFilteringByMetadata() {
    return this.committed.metadata.length > 0;
  }

  get hasChanges(): boolean {
    if (this.committed.page !== this.page) return true;
    if (this.committed.status !== this.status) return true;

    if (this.committed.searchText !== this.searchText) return true;
    if (!this.areEquals(this.metadata, this.committed.metadata)) return true;
    if (!this.areEquals(this.sortBy, this.committed.sortBy)) return true;

    return false;
  }

  commit() {
    this.committed = {
      page: this.page,
      status: this.status,
      searchText: this.searchText,
      metadata: this.metadata,
      sortBy: this.sortBy,
    };
  }

  reset() {
    this.page = this.committed.page;
    this.status = this.committed.status;
    this.searchText = this.committed.searchText;
    this.metadata = this.committed.metadata;
    this.sortBy = this.committed.sortBy;
  }

  nextPage() {
    this.page = this.committed.page + 1;
  }

  previousPage() {
    this.page = this.committed.page - 1;
  }

  private areEquals(firstArray: string[], secondArray: string[]) {
    return firstArray.join("") === secondArray.join("");
  }
}
