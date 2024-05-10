export class QuestionType extends String {
  private constructor(value: string) {
    super(value);
  }

  private get type(): string {
    return this.toLowerCase();
  }

  public static from(value: string): QuestionType {
    return new QuestionType(value);
  }

  public get isRankingType(): boolean {
    return this.type === "ranking";
  }

  public get isMultiLabelType(): boolean {
    return this.type === "multi_label_selection";
  }

  public get isSingleLabelType(): boolean {
    return this.type === "label_selection";
  }

  public get isTextType(): boolean {
    return this.type === "text";
  }

  public get isSpanType(): boolean {
    return this.type === "span";
  }

  public get isRatingType(): boolean {
    return this.type === "rating";
  }
}
