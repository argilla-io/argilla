const availableQuestionTypes = [
  "label_selection",
  "multi_label_selection",
  "ranking",
  "text",
  "span",
  "rating",
];

export type QuestionTypes =
  | "label_selection"
  | "multi_label_selection"
  | "ranking"
  | "text"
  | "span"
  | "rating";

export class QuestionType extends String {
  private constructor(value: string) {
    super(value);
  }

  public get value(): string {
    return this.toLowerCase();
  }

  public static from(value: string): QuestionType | null {
    if (availableQuestionTypes.includes(value)) {
      return new QuestionType(value);
    }

    return null;
  }

  public get isRankingType(): boolean {
    return this.value === "ranking";
  }

  public get isMultiLabelType(): boolean {
    return this.value === "multi_label_selection";
  }

  public get isSingleLabelType(): boolean {
    return this.value === "label_selection";
  }

  public get isTextType(): boolean {
    return this.value === "text";
  }

  public get isSpanType(): boolean {
    return this.value === "span";
  }

  public get isRatingType(): boolean {
    return this.value === "rating";
  }
}
