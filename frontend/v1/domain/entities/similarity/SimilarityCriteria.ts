import { Criteria } from "../common/Criteria";

export type SimilarityOrder = "most" | "least";

export interface SimilaritySearch {
  recordId: string;
  vectorName: string;
  limit: number;
  order: SimilarityOrder;
}

export class SimilarityCriteria extends Criteria {
  public recordId: string;
  public vectorName: string;
  public limit: number;
  public order: SimilarityOrder;

  complete(urlParams: string) {
    if (!urlParams) return;

    const params = urlParams.split(",");
    const [recordId, vectorName, limit, order] = params;

    this.recordId = recordId.split(":")[1];
    this.vectorName = vectorName.split(":")[1];
    this.limit = parseInt(limit.split(":")[1]);
    this.order = order.split(":")[1] as SimilarityOrder;
  }

  withValue(
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

  get urlParams(): string {
    if (!this.isCompleted) return "";

    return `record:${this.recordId},vector:${this.vectorName},limit:${this.limit},order:${this.order}`;
  }

  reset() {
    this.recordId = undefined;
    this.vectorName = undefined;
    this.limit = 50;
    this.order = "most";
  }
}
