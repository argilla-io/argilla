import { Metadata } from "../metadata/Metadata";
import { Question } from "../question/Question";

const SORT_ASC = "asc";
const SORT_DESC = "desc";

type SortOrderOptions = "asc" | "desc";

type SortOptions = "metadata" | "record" | "suggestion";

export interface SortSearch {
  key: SortOptions;
  property: string;
  question?: string;
  sort: SortOrderOptions;
}

abstract class Sort {
  public sort: SortOrderOptions = SORT_ASC;

  constructor(
    public readonly key: SortOptions,
    public readonly group: string
  ) {}

  toggleSort() {
    this.sort = this.sort === SORT_ASC ? SORT_DESC : SORT_ASC;
  }

  abstract get name(): string;

  abstract get title(): string;

  get canSort(): boolean {
    return true;
  }
}

class MetadataSort extends Sort {
  constructor(private readonly metadata: Metadata) {
    super("metadata", "metadata");
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
}

class RecordSort extends Sort {
  constructor(public readonly name: string, public readonly title = name) {
    super("record", "general");
  }
}

export class SortList {
  private categoriesSorts: Sort[] = [];
  private selectedCategories: Sort[] = [];
  private latestCommit: SortSearch[] = [];

  constructor(metadata: Metadata[], questions: Question[]) {
    this.categoriesSorts.push(new RecordSort("inserted_at"));
    this.categoriesSorts.push(new RecordSort("updated_at"));

    questions?.forEach((question) =>
      this.categoriesSorts.push(new SuggestionScoreSort(question))
    );

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

  select(category: string) {
    const found = this.findByCategory(category);

    if (found) {
      this.selectedCategories.push(found);
    }
  }

  unselect(category: string) {
    const indexOf = this.selectedCategories.findIndex(
      (categoriesSort) => categoriesSort.name === category
    );

    if (indexOf > -1) {
      this.selectedCategories.splice(indexOf, 1);
    }
  }

  replace(category: string, newCategory: string) {
    const newCategoryFound = this.findByCategory(newCategory);

    const indexOf = this.selectedCategories.findIndex(
      (categoriesSort) => categoriesSort.name === category
    );

    if (indexOf > -1) {
      this.selectedCategories.splice(indexOf, 1, newCategoryFound);
    }
  }

  clear() {
    this.selectedCategories = [];
  }

  toggleSort(category: string) {
    const found = this.findByCategory(category);
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
    return this.selectedCategories.map(({ key, name, sort }) => {
      if (key === "suggestion")
        return {
          key,
          property: "score",
          question: name,
          sort,
        };

      return {
        key,
        property: name,
        sort,
      };
    });
  }

  complete(sort: SortSearch[]) {
    if (!this.hasDifferencesWith(sort)) return;

    this.clear();

    if (!sort.length) return;

    sort.forEach(({ property, sort }) => {
      const found = this.findByCategory(property);

      if (found) {
        found.sort = sort;

        this.selectedCategories.push(found);
      }
    });

    this.commit();
  }

  private findByCategory(category: string) {
    return this.categoriesSorts.find((m) => m.name === category);
  }
}
