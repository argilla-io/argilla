import { Criteria } from "../common/Criteria";

const DEFAULT_RECORDS_TO_FETCH = 10;

interface BrowserPagination {
  page: number;
  many: number;
}

interface ServerPagination {
  from: number;
  many: number;
}

export class PageCriteria extends Criteria {
  public readonly options = [10, 25, 50, 100];

  public mode: "focus" | "bulk" = "focus";
  public client: BrowserPagination;
  private _server: ServerPagination;

  constructor() {
    super();

    this.reset();
  }

  get server(): ServerPagination {
    return {
      ...this._server,
    };
  }

  get next(): number {
    if (this.isBulkMode) return this.client.page + this.client.many;

    return this.client.page + 1;
  }

  get previous(): number {
    if (this.isBulkMode)
      return Math.max(this.client.page - this.client.many, 1);

    return this.client.page - 1;
  }

  get isBulkMode() {
    return this.mode === "bulk";
  }

  get isFocusMode() {
    return this.mode === "focus";
  }

  get urlParams(): string {
    if (this.isFocusMode) return this.client.page.toString();

    return `${this.client.page}~${this.client.many}`;
  }

  get buffer(): number {
    if (this.isBulkMode) return this.client.many;

    return this.client.many / 2;
  }

  withValue({ client, mode }: PageCriteria) {
    this.client = {
      page: client.page,
      many: client.many,
    };

    this.mode = mode;
  }

  complete(urlParams = "") {
    const pageParams = urlParams
      .split("~")
      .filter((param) => !isNaN(Number(param)) && param !== "");

    if (pageParams.length === 0) return;

    if (pageParams.length === 2) {
      const [page, many] = pageParams;

      if (!this.options.includes(Number(many))) return;

      this.client = {
        page: Number(page),
        many: Number(many),
      };
      this.mode = "bulk";
    } else {
      const [page] = pageParams;

      this.client = {
        page: Number(page),
        many: DEFAULT_RECORDS_TO_FETCH,
      };
    }
  }

  reset() {
    this.client = {
      page: 1,
      many: DEFAULT_RECORDS_TO_FETCH,
    };

    this._server = {
      from: this.client.page,
      many: this.client.many,
    };
  }

  synchronizePagination(server: ServerPagination) {
    this._server = {
      ...server,
    };
  }

  goTo(page: number, many: number = this.client.many) {
    this.client = {
      page,
      many,
    };
  }

  goToFirst(many?: number) {
    this.goTo(1, many);
  }

  isFirstPage() {
    return this.client.page === 1;
  }

  bulkMode() {
    this.mode = "bulk";

    this.reset();
  }

  focusMode() {
    this.mode = "focus";

    this.reset();
  }
}
