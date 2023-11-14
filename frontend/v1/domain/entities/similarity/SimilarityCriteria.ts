export type SimilarityOrder = "most" | "least";

export class SimilarityCriteria {
  public recordId: string;
  public vectorName: string;
  public limit: number;
  public order: SimilarityOrder;

  constructor() {
    this.reset();
  }

  complete(
    recordId: string,
    vectorName: string,
    limit: number,
    order: SimilarityOrder
  ) {
    if (!recordId && !vectorName && !limit && !order) return;

    this.recordId = recordId;
    this.vectorName = vectorName;
    this.limit = limit;
    this.order = order;
  }

  get isCompleted() {
    return (
      this.recordId !== undefined &&
      this.vectorName !== undefined &&
      this.limit !== undefined &&
      this.order !== undefined
    );
  }

  reset() {
    this.recordId = undefined;
    this.vectorName = undefined;
    this.limit = 50;
    this.order = "most";
  }

  isEqual(other: SimilarityCriteria): boolean {
    return (
      this.recordId === other.recordId &&
      this.vectorName === other.vectorName &&
      this.limit === other.limit &&
      this.order === other.order
    );
  }
}
