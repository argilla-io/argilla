import { SimilarityCriteria } from "../similarity/SimilarityCriteria";
import { SortCriteria } from "../sort/SortCriteria";
import { MetadataCriteria } from "../metadata/MetadataCriteria";
import { ResponseCriteria } from "../response/ResponseCriteria";
import { SuggestionCriteria } from "../suggestion/SuggestionCriteria";
import { PageCriteria } from "../page/PageCriteria";
import { SearchTextCriteria } from "../search/SearchTextCriteria";
import { RecordStatus } from "./RecordAnswer";

interface IRecordCriteria {
  readonly page: PageCriteria;
  readonly status: RecordStatus;
  readonly searchText: SearchTextCriteria;
  readonly metadata: MetadataCriteria;
  readonly sortBy: SortCriteria;
  readonly response: ResponseCriteria;
  readonly suggestion: SuggestionCriteria;
  readonly similaritySearch: SimilarityCriteria;
}

class CommittedRecordCriteria implements IRecordCriteria {
  public readonly page: PageCriteria;
  public readonly status: RecordStatus;
  public readonly searchText: SearchTextCriteria;
  public readonly metadata: MetadataCriteria;
  public readonly sortBy: SortCriteria;
  public readonly response: ResponseCriteria;
  public readonly suggestion: SuggestionCriteria;
  public readonly similaritySearch: SimilarityCriteria;

  constructor(recordCriteria: IRecordCriteria) {
    const pageCommitted = new PageCriteria();
    const searchTextCommitted = new SearchTextCriteria();
    const similaritySearchCommitted = new SimilarityCriteria();
    const metadataCommitted = new MetadataCriteria();
    const sortByCommitted = new SortCriteria();
    const responseCommitted = new ResponseCriteria();
    const suggestionCommitted = new SuggestionCriteria();

    pageCommitted.withValue(recordCriteria.page);
    searchTextCommitted.withValue(recordCriteria.searchText);
    metadataCommitted.withValue(recordCriteria.metadata);
    sortByCommitted.withValue(recordCriteria.sortBy);
    suggestionCommitted.withValue(recordCriteria.suggestion);
    responseCommitted.withValue(recordCriteria.response);
    similaritySearchCommitted.withValue(recordCriteria.similaritySearch);

    this.status = recordCriteria.status;
    this.searchText = searchTextCommitted;
    this.page = pageCommitted;
    this.metadata = metadataCommitted;
    this.sortBy = sortByCommitted;
    this.response = responseCommitted;
    this.suggestion = suggestionCommitted;
    this.similaritySearch = similaritySearchCommitted;
  }

  get isPending() {
    return this.status === "pending";
  }
}

export class RecordCriteria implements IRecordCriteria {
  public isChangingAutomatically = false;
  public committed: CommittedRecordCriteria;
  public previous?: CommittedRecordCriteria;

  public page: PageCriteria;
  public searchText: SearchTextCriteria;
  public metadata: MetadataCriteria;
  public sortBy: SortCriteria;
  public response: ResponseCriteria;
  public suggestion: SuggestionCriteria;
  public similaritySearch: SimilarityCriteria;

  constructor(
    public readonly datasetId: string,
    page: string,
    public status: RecordStatus,
    searchText: string,
    metadata: string,
    sortBy: string,
    response: string,
    suggestion: string,
    similaritySearch: string
  ) {
    this.page = new PageCriteria();
    this.searchText = new SearchTextCriteria();
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
    return this.searchText.isCompleted;
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
    return this.committed.searchText.isCompleted;
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

  get isComingToBulkMode(): boolean {
    return (
      (!this.previous || this.previous.page.isFocusMode) &&
      this.committed.page.isBulkMode
    );
  }

  get hasChanges(): boolean {
    return this.areDifferent(this, this.committed);
  }

  get isPaginatingForward() {
    return this.page.client.page > this.previous?.page.client.page;
  }

  get isPaginatingBackward() {
    return this.page.client.page < this.previous?.page.client.page;
  }

  complete(
    page: string,
    status: RecordStatus,
    searchText: string,
    metadata: string,
    sortBy: string,
    response: string,
    suggestion: string,
    similaritySearch: string
  ) {
    this.isChangingAutomatically = true;

    this.status = status ?? "pending";

    this.page.complete(page);
    this.searchText.complete(searchText);
    this.metadata.complete(metadata);
    this.sortBy.complete(sortBy);
    this.response.complete(response);
    this.suggestion.complete(suggestion);
    this.similaritySearch.complete(similaritySearch);
  }

  commit() {
    if (this.committed) {
      this.previous = new CommittedRecordCriteria(this.committed);
    }

    this.committed = new CommittedRecordCriteria(this);

    if (!this.areDifferent(this.committed, this.previous)) {
      this.previous = null;
    }

    this.isChangingAutomatically = false;
  }

  rollback() {
    this.status = this.committed.status;

    this.page.withValue(this.committed.page);
    this.searchText.withValue(this.committed.searchText);
    this.metadata.withValue(this.committed.metadata);
    this.sortBy.withValue(this.committed.sortBy);
    this.response.withValue(this.committed.response);
    this.suggestion.withValue(this.committed.suggestion);
    this.similaritySearch.withValue(this.committed.similaritySearch);
  }

  reset() {
    // Not call the similaritySearch.reset() because it is not managed as a global filter.
    // Not clear the searchText because it is not managed as a global filter.

    this.page.reset();
    this.metadata.reset();
    this.sortBy.reset();
    this.response.reset();
    this.suggestion.reset();
  }

  clone() {
    return new RecordCriteria(
      this.datasetId,
      this.page.urlParams,
      this.status,
      this.searchText.urlParams,
      this.metadata.urlParams,
      this.sortBy.urlParams,
      this.response.urlParams,
      this.suggestion.urlParams,
      this.similaritySearch.urlParams
    );
  }

  get queuePage(): number {
    return this.isFilteringBySimilarity
      ? this.page.server.from
      : this.page.client.page;
  }

  nextPage() {
    this.page.goTo(this.committed.page.next);
  }

  previousPage() {
    this.page.goTo(this.committed.page.previous);
  }

  private areDifferent(previous: IRecordCriteria, actual: IRecordCriteria) {
    if (!previous) return false;
    if (!actual) return false;

    if (actual.status !== previous.status) return true;

    if (!previous.searchText.isEqual(actual.searchText)) return true;
    if (!previous.page.isEqual(actual.page)) return true;
    if (!previous.searchText.isEqual(actual.searchText)) return true;
    if (!previous.metadata.isEqual(actual.metadata)) return true;
    if (!previous.sortBy.isEqual(actual.sortBy)) return true;
    if (!previous.response.isEqual(actual.response)) return true;
    if (!previous.suggestion.isEqual(actual.suggestion)) return true;
    if (!previous.similaritySearch.isEqual(actual.similaritySearch))
      return true;

    return false;
  }
}
