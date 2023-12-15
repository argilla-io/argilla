import { SimilarityCriteria } from "../similarity/SimilarityCriteria";
import { SortCriteria } from "../sort/SortCriteria";
import { MetadataCriteria } from "../metadata/MetadataCriteria";
import { ResponseCriteria } from "../response/ResponseCriteria";
import { SuggestionCriteria } from "../suggestion/SuggestionCriteria";
import { PageCriteria } from "../page/PageCriteria";
import { RecordStatus } from "./RecordAnswer";

class CommittedRecordCriteria {
  public readonly page: PageCriteria;
  public readonly status: RecordStatus;
  public readonly searchText: string;
  public readonly metadata: MetadataCriteria;
  public readonly sortBy: SortCriteria;
  public readonly response: ResponseCriteria;
  public readonly suggestion: SuggestionCriteria;
  public readonly similaritySearch: SimilarityCriteria;

  constructor(private readonly recordCriteria: RecordCriteria) {
    const pageCommitted = new PageCriteria();
    const similaritySearchCommitted = new SimilarityCriteria();
    const metadataCommitted = new MetadataCriteria();
    const sortByCommitted = new SortCriteria();
    const responseCommitted = new ResponseCriteria();
    const suggestionCommitted = new SuggestionCriteria();

    pageCommitted.withValue(this.recordCriteria.page);
    metadataCommitted.withValue(this.recordCriteria.metadata);
    sortByCommitted.withValue(this.recordCriteria.sortBy);
    suggestionCommitted.withValue(this.recordCriteria.suggestion);
    responseCommitted.withValue(this.recordCriteria.response);
    similaritySearchCommitted.withValue(this.recordCriteria.similaritySearch);

    this.status = this.recordCriteria.status;
    this.searchText = this.recordCriteria.searchText;
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

export class RecordCriteria {
  public isChangingAutomatically = false;
  public committed: CommittedRecordCriteria;

  public page: PageCriteria;
  public metadata: MetadataCriteria;
  public sortBy: SortCriteria;
  public response: ResponseCriteria;
  public suggestion: SuggestionCriteria;
  public similaritySearch: SimilarityCriteria;

  constructor(
    public readonly datasetId: string,
    page: string,
    public status: RecordStatus,
    public searchText: string,
    metadata: string,
    sortBy: string,
    response: string,
    suggestion: string,
    similaritySearch: string
  ) {
    this.page = new PageCriteria();
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
    if (this.committed.status !== this.status) return true;
    if (this.committed.searchText !== this.searchText) return true;

    if (!this.page.isEqual(this.committed.page)) return true;
    if (!this.metadata.isEqual(this.committed.metadata)) return true;
    if (!this.sortBy.isEqual(this.committed.sortBy)) return true;
    if (!this.response.isEqual(this.committed.response)) return true;
    if (!this.suggestion.isEqual(this.committed.suggestion)) return true;
    if (!this.similaritySearch.isEqual(this.committed.similaritySearch))
      return true;

    return false;
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
    this.searchText = searchText ?? "";

    this.page.complete(page);
    this.metadata.complete(metadata);
    this.sortBy.complete(sortBy);
    this.response.complete(response);
    this.suggestion.complete(suggestion);
    this.similaritySearch.complete(similaritySearch);
  }

  commit() {
    this.committed = new CommittedRecordCriteria(this);

    this.isChangingAutomatically = false;
  }

  rollback() {
    this.status = this.committed.status;
    this.searchText = this.committed.searchText;

    this.page.withValue(this.committed.page);
    this.metadata.withValue(this.committed.metadata);
    this.sortBy.withValue(this.committed.sortBy);
    this.response.withValue(this.committed.response);
    this.suggestion.withValue(this.committed.suggestion);
    this.similaritySearch.withValue(this.committed.similaritySearch);
  }

  reset() {
    // TODO: Review why the similarity is not calling here...

    this.page.reset();
    this.metadata.reset();
    this.sortBy.reset();
    this.response.reset();
    this.suggestion.reset();
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
}
