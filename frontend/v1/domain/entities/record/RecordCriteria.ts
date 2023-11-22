import { SimilarityCriteria } from "../similarity/SimilarityCriteria";
import { SortCriteria } from "../sort/SortCriteria";
import { MetadataCriteria } from "../metadata/MetadataCriteria";
import { ResponseCriteria } from "../response/ResponseCriteria";
import { SuggestionCriteria } from "../suggestion/SuggestionCriteria";
import { RecordStatus } from "./RecordAnswer";

interface CommittedRecordCriteria {
  page: number;
  status: RecordStatus;
  searchText: string;
  metadata: MetadataCriteria;
  sortBy: SortCriteria;
  response: ResponseCriteria;
  suggestion: SuggestionCriteria;
  similaritySearch: SimilarityCriteria;
}

export class RecordCriteria {
  public isChangingAutomatically = false;
  public committed: CommittedRecordCriteria;

  public metadata: MetadataCriteria;
  public sortBy: SortCriteria;
  public response: ResponseCriteria;
  public suggestion: SuggestionCriteria;
  public similaritySearch: SimilarityCriteria;

  constructor(
    public readonly datasetId: string,
    public page: number,
    public status: RecordStatus,
    public searchText: string,
    metadata: string,
    sortBy: string,
    response: string,
    suggestion: string,
    similaritySearch: string
  ) {
    this.metadata = new MetadataCriteria();
    this.sortBy = new SortCriteria();
    this.response = new ResponseCriteria();
    this.suggestion = new SuggestionCriteria();
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

  get isFilteringByResponse() {
    return this.response.isCompleted;
  }

  get isFilteringBySuggestion() {
    return this.suggestion.isCompleted;
  }

  get isFilteringByMetadata() {
    return this.metadata.isCompleted;
  }

  get isSortingBy() {
    return this.sortBy.isCompleted;
  }

  get isFilteringByAdvanceSearch() {
    return (
      this.isFilteringByText ||
      this.isFilteringByMetadata ||
      this.isFilteringBySimilarity ||
      this.isFilteringByResponse ||
      this.isFilteringBySuggestion ||
      this.isSortingBy
    );
  }

  get isFilteredByText() {
    return this.committed.searchText.length > 0;
  }

  get isFilteredByMetadata() {
    return this.committed.metadata.isCompleted;
  }

  get isFilteredByResponse() {
    return this.committed.response.isCompleted;
  }

  get isFilteredBySuggestion() {
    return this.committed.suggestion.isCompleted;
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

    if (!this.metadata.isEqual(this.committed.metadata)) return true;
    if (!this.sortBy.isEqual(this.committed.sortBy)) return true;
    if (!this.response.isEqual(this.committed.response)) return true;
    if (!this.suggestion.isEqual(this.committed.suggestion)) return true;
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
    response: string,
    suggestion: string,
    similaritySearch: string
  ) {
    this.isChangingAutomatically = true;

    this.page = Number(page ?? 1);
    this.status = status ?? "pending";
    this.searchText = searchText ?? "";

    this.metadata.complete(metadata);
    this.sortBy.complete(sortBy);
    this.response.complete(response);
    this.suggestion.complete(suggestion);
    this.similaritySearch.complete(similaritySearch);
  }

  commit() {
    // TODO: Move to instance of commit
    const similaritySearchCommitted = new SimilarityCriteria();
    const metadataCommitted = new MetadataCriteria();
    const sortByCommitted = new SortCriteria();
    const responseCommitted = new ResponseCriteria();
    const suggestionCommitted = new SuggestionCriteria();

    similaritySearchCommitted.withValue(
      this.similaritySearch.recordId,
      this.similaritySearch.vectorName,
      this.similaritySearch.limit,
      this.similaritySearch.order
    );
    metadataCommitted.withValue(this.metadata.value);
    sortByCommitted.witValue(this.sortBy.value);
    responseCommitted.withValue(this.response.value);
    suggestionCommitted.withValue(this.suggestion.value);

    this.committed = {
      page: this.page,
      status: this.status,
      searchText: this.searchText,

      metadata: metadataCommitted,
      sortBy: sortByCommitted,
      response: responseCommitted,
      suggestion: suggestionCommitted,
      similaritySearch: similaritySearchCommitted,
    };

    this.isChangingAutomatically = false;
  }

  rollback() {
    this.page = this.committed.page;
    this.status = this.committed.status;
    this.searchText = this.committed.searchText;
    this.metadata = this.committed.metadata;

    this.metadata.withValue(this.committed.metadata.value);
    this.sortBy.witValue(this.committed.sortBy.value);
    this.response.withValue(this.committed.response.value);
    this.suggestion.withValue(this.committed.suggestion.value);
    this.similaritySearch.withValue(
      this.committed.similaritySearch.recordId,
      this.committed.similaritySearch.vectorName,
      this.committed.similaritySearch.limit,
      this.committed.similaritySearch.order
    );
  }

  reset() {
    this.metadata.reset();
    this.sortBy.reset();
    this.response.reset();
    this.suggestion.reset();
  }

  nextPage() {
    this.page = this.committed.page + 1;
  }

  previousPage() {
    this.page = this.committed.page - 1;
  }
}
