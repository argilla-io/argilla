type OrderSimilarity = "most" | "least";

export class SimilarityCriteria {
  public recordId: string;
  public vectorId: string;
  public limit: number;
  public order: OrderSimilarity;

  constructor() {
    this.limit = 50;
    this.order = "most";
  }

  complete(
    recordId: string,
    vectorId: string,
    limit: number,
    order: OrderSimilarity
  ) {
    this.recordId = recordId;
    this.vectorId = vectorId;
    this.limit = limit;
    this.order = order;
  }

  get isCompleted() {
    return (
      this.recordId !== undefined &&
      this.vectorId !== undefined &&
      this.limit !== undefined &&
      this.order !== undefined
    );
  }

  isEqual(other: SimilarityCriteria): boolean {
    return (
      this.recordId === other.recordId &&
      this.vectorId === other.vectorId &&
      this.limit === other.limit &&
      this.order === other.order
    );
  }
}
