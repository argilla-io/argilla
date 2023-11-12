import { SimilarityCriteria } from "../similarity/SimilarityCriteria";
import { SortCriteria } from "../metadata/SortCriteria";
import { MetadataCriteria } from "../metadata/MetadataCriteria";
import { RecordStatus } from "./RecordAnswer";

interface CommittedRecordCriteria {
  page: number;
  status: RecordStatus;
  searchText: string;
  metadata: MetadataCriteria;
  sortBy: SortCriteria;
  response: string[];
  suggestion: string[];
  similaritySearch: SimilarityCriteria;
}

export class RecordCriteria {
  public isChangingAutomatically = false;
  public committed: CommittedRecordCriteria;

  public metadata: MetadataCriteria;
  public sortBy: SortCriteria;
  public similaritySearch: SimilarityCriteria;

  constructor(
    public readonly datasetId: string,
    public page: number,
    public status: RecordStatus,
    public searchText: string,
    metadata: string,
    sortBy: string,
    public response: string[],
    public suggestion: string[],
    similaritySearch: string
  ) {
    this.metadata = new MetadataCriteria();
    this.sortBy = new SortCriteria();
    this.similaritySearch = new SimilarityCriteria();

    this.complete(
      page,
      status,
      searchText,
      metadata,
      sortBy,
      response,
      suggestion,
      similaritySearch
    );

    this.commit();
  }

  get isFilteringByText() {
    return this.searchText.length > 0;
  }

  get isFilteringBySimilarity() {
    return this.similaritySearch.isCompleted;
  }

  get isFilteredByText() {
    return this.committed.searchText.length > 0;
  }

  get isFilteredByMetadata() {
    return this.committed.metadata.isCompleted;
  }

  get isSortedBy() {
    return this.committed.sortBy.isCompleted;
  }

  get isFilteredBySimilarity() {
    return this.committed.similaritySearch.isCompleted;
  }

  get hasChanges(): boolean {
    if (this.committed.page !== this.page) return true;
    if (this.committed.status !== this.status) return true;

    if (this.committed.searchText !== this.searchText) return true;
    if (!this.areEquals(this.response, this.committed.response)) return true;
    if (!this.areEquals(this.suggestion, this.committed.suggestion))
      return true;

    if (!this.metadata.isEqual(this.committed.metadata)) return true;
    if (!this.sortBy.isEqual(this.committed.sortBy)) return true;
    if (!this.similaritySearch.isEqual(this.committed.similaritySearch))
      return true;

    return false;
  }

  complete(
    page: number,
    status: RecordStatus,
    searchText: string,
    metadata: string,
    sortBy: string,
    response: string[],
    suggestion: string[],
    similaritySearch: string
  ) {
    this.isChangingAutomatically = true;

    this.page = Number(page ?? 1);
    this.status = status ?? "pending";
    this.searchText = searchText ?? "";
    this.response = response ?? [];
    this.suggestion = suggestion ?? [];

    this.metadata.complete(metadata);
    this.sortBy.complete(sortBy);
    this.similaritySearch.complete(similaritySearch);
  }

  commit() {
    // TODO: Move to instance of commit
    const similaritySearchCommitted = new SimilarityCriteria();
    const metadataCommitted = new MetadataCriteria();
    const sortByCommitted = new SortCriteria();

    similaritySearchCommitted.withValue(
      this.similaritySearch.recordId,
      this.similaritySearch.vectorName,
      this.similaritySearch.limit,
      this.similaritySearch.order
    );
    metadataCommitted.withValue(this.metadata.value);
    sortByCommitted.witValue(this.sortBy.value);

    this.committed = {
      page: this.page,
      status: this.status,
      searchText: this.searchText,
      response: this.response,
      suggestion: this.suggestion,
      metadata: metadataCommitted,
      sortBy: sortByCommitted,
      similaritySearch: similaritySearchCommitted,
    };

    this.isChangingAutomatically = false;
  }

  rollback() {
    this.page = this.committed.page;
    this.status = this.committed.status;
    this.searchText = this.committed.searchText;
    this.metadata = this.committed.metadata;
    this.response = this.committed.response;
    this.suggestion = this.committed.suggestion;

    this.metadata.withValue(this.committed.metadata.value);
    this.sortBy.witValue(this.committed.sortBy.value);
    this.similaritySearch.withValue(
      this.committed.similaritySearch.recordId,
      this.committed.similaritySearch.vectorName,
      this.committed.similaritySearch.limit,
      this.committed.similaritySearch.order
    );
  }

  reset() {
    this.response = [];
    this.suggestion = [];
    this.metadata.reset();
    this.sortBy.reset();
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
