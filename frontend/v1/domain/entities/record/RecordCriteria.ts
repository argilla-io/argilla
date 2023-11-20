import { SimilarityCriteria } from "../similarity/SimilarityCriteria";
import { RecordStatus } from "./RecordAnswer";

interface CommittedRecordCriteria {
  page: number;
  status: RecordStatus;
  searchText: string;
  metadata: string[];
  sortBy: string[];
  similaritySearch: SimilarityCriteria;
}

export class RecordCriteria {
  public isChangingAutomatically = false;
  public committed: CommittedRecordCriteria;
  public page: number;
  public status: RecordStatus;
  private _similaritySearch: SimilarityCriteria;

  constructor(
    public readonly datasetId: string,
    page: number,
    status: RecordStatus,
    public searchText: string,
    public metadata: string[],
    public sortBy: string[],
    similaritySearch: string
  ) {
    this.complete(page, status, searchText, metadata, sortBy, similaritySearch);

    this.commit();
  }

  get similaritySearch() {
    return this._similaritySearch;
  }

  get isFilteredByText() {
    return this.committed.searchText.length > 0;
  }

  get isFilteredByMetadata() {
    return this.committed.metadata.length > 0;
  }

  get isFilteringByText() {
    return this.searchText.length > 0;
  }

  get isFilteringBySimilarity() {
    return this.similaritySearch.isCompleted;
  }

  get isFilteredBySimilarity() {
    return this.committed.similaritySearch.isCompleted;
  }

  get isSortedBy() {
    return this.committed.sortBy.length > 0;
  }

  get hasChanges(): boolean {
    if (this.committed.page !== this.page) return true;
    if (this.committed.status !== this.status) return true;

    if (this.committed.searchText !== this.searchText) return true;
    if (!this.areEquals(this.metadata, this.committed.metadata)) return true;
    if (!this.areEquals(this.sortBy, this.committed.sortBy)) return true;
    if (!this.similaritySearch.isEqual(this.committed.similaritySearch))
      return true;

    return false;
  }

  complete(
    page: number,
    status: RecordStatus,
    searchText: string,
    metadata: string[],
    sortBy: string[],
    similaritySearch: string
  ) {
    this.isChangingAutomatically = true;

    this.page = page ? Number(page) : 1;
    this.status = status || "pending";
    this.searchText = searchText ?? "";
    this.metadata = metadata ?? [];
    this.sortBy = sortBy ?? [];
    this._similaritySearch = new SimilarityCriteria();

    if (similaritySearch) {
      try {
        const parsed = JSON.parse(similaritySearch);

        this.similaritySearch.complete(
          parsed.recordId,
          parsed.vectorName,
          parsed.limit,
          parsed.order
        );
      } catch (error) {
        // User has manually changed the URL, it's ok to ignore this error
      }
    }
  }

  commit() {
    const similaritySearchCommitted = new SimilarityCriteria();
    similaritySearchCommitted.complete(
      this.similaritySearch.recordId,
      this.similaritySearch.vectorName,
      this.similaritySearch.limit,
      this.similaritySearch.order
    );

    this.committed = {
      page: this.page,
      status: this.status,
      searchText: this.searchText,
      metadata: this.metadata,
      sortBy: this.sortBy,
      similaritySearch: similaritySearchCommitted,
    };

    this.isChangingAutomatically = false;
  }

  reset() {
    this.page = this.committed.page;
    this.status = this.committed.status;
    this.searchText = this.committed.searchText;
    this.metadata = this.committed.metadata;
    this.sortBy = this.committed.sortBy;

    this.similaritySearch.complete(
      this.committed.similaritySearch.recordId,
      this.committed.similaritySearch.vectorName,
      this.committed.similaritySearch.limit,
      this.committed.similaritySearch.order
    );
  }

  resetFiltersAndSortBy() {
    this.metadata = [];
    this.sortBy = [];
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
