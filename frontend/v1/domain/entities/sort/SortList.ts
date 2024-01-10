import { Metadata } from "../metadata/Metadata";
import { Question } from "../question/Question";

const SORT_ASC = "asc";
const SORT_DESC = "desc";

type SortOrderOptions = "asc" | "desc";

type SortOptions = "metadata" | "record" | "suggestion" | "response";

type SortProperty = "score" | "value";

type SortId = string;

export interface SortSearch {
  entity: SortOptions;
  name: string;
  property?: SortProperty;
  order: SortOrderOptions;
}

abstract class Sort {
  public sort: SortOrderOptions = SORT_ASC;

  constructor(
    public readonly key: SortOptions,
    public readonly property?: SortProperty
  ) {}

  toggleSort() {
    this.sort = this.sort === SORT_ASC ? SORT_DESC : SORT_ASC;
  }

  abstract get name(): string;

  abstract get title(): string;

  get id(): SortId {
    return this.property
      ? `${this.key}.${this.name}.${this.property}`
      : `${this.key}.${this.name}`;
  }

  get group(): string {
    return this.property ? `${this.key}.${this.property}` : this.key;
  }

  get canSort(): boolean {
    return true;
  }

  get tooltip() {
    return this.title;
  }
}
type SortIdentifier = Pick<Sort, "key" | "name" | "property">;

class MetadataSort extends Sort {
  constructor(private readonly metadata: Metadata) {
    super("metadata");
  }

  get name() {
    return this.metadata.name;
  }

  get title() {
    return this.metadata.title;
  }

  get canSort(): boolean {
    return this.metadata.hasValues;
  }
}

class SuggestionScoreSort extends Sort {
  constructor(private readonly question: Question) {
    super("suggestion", "score");
  }

  get name() {
    return this.question.name;
  }

  get title() {
    return this.question.name;
  }

  get tooltip() {
    return this.question.title;
  }
}

class SuggestionValueSort extends Sort {
  constructor(private readonly question: Question) {
    super("suggestion", "value");
  }

  get name() {
    return this.question.name;
  }

  get title() {
    return this.question.name;
  }

  get tooltip() {
    return this.question.title;
  }
}

class ResponseValueSort extends Sort {
  constructor(private readonly question: Question) {
    super("response");
  }

  get name() {
    return this.question.name;
  }

  get title() {
    return this.question.name;
  }

  get tooltip() {
    return this.question.title;
  }
}

class RecordSort extends Sort {
  constructor(public readonly name: string, public readonly title = name) {
    super("record");
  }
}

export class SortList {
  private categoriesSorts: Sort[] = [];
  private selectedCategories: Sort[] = [];
  private latestCommit: SortSearch[] = [];

  constructor(metadata: Metadata[], questions: Question[]) {
    this.categoriesSorts.push(new RecordSort("inserted_at"));
    this.categoriesSorts.push(new RecordSort("updated_at"));

    questions?.forEach((q) =>
      this.categoriesSorts.push(new SuggestionScoreSort(q))
    );

    questions
      ?.filter((q) => q.isRatingType)
      .forEach((q) => this.categoriesSorts.push(new SuggestionValueSort(q)));

    questions
      ?.filter((q) => q.isRatingType)
      .forEach((q) => this.categoriesSorts.push(new ResponseValueSort(q)));

    metadata?.forEach((metadata) =>
      this.categoriesSorts.push(new MetadataSort(metadata))
    );
  }

  get selected() {
    return this.selectedCategories;
  }

  get noSelected() {
    return this.categoriesSorts.filter(
      (metadata) => !this.selectedCategories.includes(metadata)
    );
  }

  select(sort: SortIdentifier) {
    const found = this.findByCategory(sort);

    if (found) {
      this.selectedCategories.push(found);
    }
  }

  unselect(sort: SortIdentifier) {
    const indexOf = this.findIndexSelectedCategory(sort);

    if (indexOf > -1) {
      this.selectedCategories.splice(indexOf, 1);
    }
  }

  replace(actualSort: SortIdentifier, newSort: SortIdentifier) {
    const newCategoryFound = this.findByCategory(newSort);

    const indexOf = this.findIndexSelectedCategory(actualSort);

    if (indexOf > -1) {
      this.selectedCategories.splice(indexOf, 1, newCategoryFound);
    }
  }

  clear() {
    this.selectedCategories = [];
  }

  toggleSort(sort: SortIdentifier) {
    const found = this.findByCategory(sort);

    if (found) found.toggleSort();
  }

  get hasChanges() {
    return this.hasDifferencesWith(this.createSortCriteria());
  }

  hasDifferencesWith(compare: SortSearch[]) {
    return JSON.stringify(this.latestCommit) !== JSON.stringify(compare);
  }

  commit(): SortSearch[] {
    this.latestCommit = this.createSortCriteria();

    return this.latestCommit;
  }

  private createSortCriteria(): SortSearch[] {
    return this.selectedCategories.map(
      ({ key: entity, property, name, sort: order }) => {
        if (property)
          return {
            entity,
            name,
            property,
            order,
          };

        return {
          entity,
          name,
          order,
        };
      }
    );
  }

  complete(sort: SortSearch[]) {
    if (!this.hasDifferencesWith(sort)) return;

    this.clear();

    if (!sort.length) return;

    sort.forEach(({ entity, name, order, property }) => {
      const found = this.findByCategory({
        key: entity,
        name,
        property,
      });

      if (found) {
        found.sort = order;

        this.selectedCategories.push(found);
      }
    });

    this.commit();
  }

  private findByCategory(sort: SortIdentifier) {
    return this.categoriesSorts.find((s) => s.id === this.toId(sort));
  }

  private findIndexSelectedCategory(sort: SortIdentifier) {
    return this.selectedCategories.findIndex((s) => s.id === this.toId(sort));
  }

  private toId(sort: SortIdentifier) {
    if (sort.property) return `${sort.key}.${sort.name}.${sort.property}`;

    return `${sort.key}.${sort.name}`;
  }
}
