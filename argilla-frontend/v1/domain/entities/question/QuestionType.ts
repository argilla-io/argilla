export class QuestionType extends String {
  private constructor(value: string) {
    super(value);
  }

  public get value(): string {
    return this.toLowerCase();
  }

  public static from(value: string): QuestionType {
    return new QuestionType(value);
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
