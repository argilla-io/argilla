import { Criteria } from "../common/Criteria";

interface SearchText {
  text: string;
  field: string;
}

export class SearchTextCriteria extends Criteria {
  public value: SearchText;

  constructor() {
    super();

    this.reset();
  }

  complete(urlParams: string) {
    if (!urlParams) return;

    const splitted = urlParams.split("~");

    if (splitted.length > 2) {
      const [field, ...text] = splitted.reverse();

      return this.setValue(text.reverse().join("~"), field);
    }

    const [text, field] = splitted;

    this.setValue(
      text
        .split("")
        .map((char, i) =>
          this.itWasConvertedToUnderscore(text, char, i) ? " " : char
        )
        .join(""),
      field
    );
  }

  withValue(searchTextCriteria: SearchTextCriteria) {
    this.setValue(
      searchTextCriteria.value.text,
      searchTextCriteria.value.field
    );
  }

  reset() {
    this.setValue("", "all");
  }

  get isCompleted(): boolean {
    return this.value.text.length > 0;
  }

  get urlParams(): string {
    if (!this.isCompleted) return "";

    if (!this.value.field?.length) {
      this.value.field = "all";
    }

    return `${this.value.text.replaceAll(" ", "_")}~${this.value.field}`;
  }

  get isFilteringByField() {
    return this.value.field !== "all";
  }

  private setValue(text: string, field: string) {
    this.value = {
      text: text ?? "",
      field: field ?? "all",
    };
  }

  private itWasConvertedToUnderscore(text: string, char: string, i: number) {
    return (
      char === "_" &&
      !!text[i + 1] &&
      text[i + 1] !== "_" &&
      !!text[i - 1] &&
      text[i - 1] !== "_"
    );
  }
}
