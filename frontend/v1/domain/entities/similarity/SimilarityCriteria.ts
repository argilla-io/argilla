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

    const params = urlParams.split(".");
    if (params.length !== 8) return;

    this.recordId = params[1];
    this.vectorName = params[3];
    this.limit = parseInt(params[5]);
    this.order = params[7] as SimilarityOrder;
  }

  withValue(similarityCriteria: SimilarityCriteria) {
    const { recordId, vectorName, limit, order } = similarityCriteria;

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

    return `record.${this.recordId}.vector.${this.vectorName}.limit.${this.limit}.order.${this.order}`;
  }

  reset() {
    this.recordId = undefined;
    this.vectorName = undefined;
    this.limit = 50;
    this.order = "most";
  }
}
