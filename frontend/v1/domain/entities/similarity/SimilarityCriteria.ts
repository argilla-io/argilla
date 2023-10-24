export type SimilarityOrder = "most" | "least";

export class SimilarityCriteria {
  public recordId: string;
  public vectorId: string;
  public limit: number;
  public order: SimilarityOrder;

  constructor() {
    this.reset();
  }

  complete(
    recordId: string,
    vectorId: string,
    limit: number,
    order: SimilarityOrder
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

  reset() {
    this.recordId = undefined;
    this.vectorId = undefined;
    this.limit = 50;
    this.order = "most";
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
