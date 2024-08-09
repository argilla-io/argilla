export type BackendRankingAnswer = { value: string; rank: number };

export type BackendAnswerCombinations =
  | string
  | string[]
  | number
  | BackendRankingAnswer[];

interface BackendSuggestion {
  id: string;
  question_id: string;
  value: BackendAnswerCombinations;
  score: number;
  agent: string;
}
export type BackendRecordStatus = "submitted" | "discarded" | "draft";

export interface BackendResponseRequest {
  status: BackendRecordStatus;
  values: BackendAnswerCombinations;
}

export interface BackendResponseResponse {
  id: string;
  status: BackendRecordStatus;
  values: BackendAnswerCombinations;
  updated_at: string;
}

export interface BackendRecord {
  id: string;
  suggestions: BackendSuggestion[];
  responses: BackendResponseResponse[];
  fields: { [key: string]: string | any };
  updated_at: Date;
  inserted_at: Date;
  metadata?: { [key: string]: string };
  status: "pending" | "completed";
  query_score: number;
}

export interface BackendRecords {
  records: BackendRecord[];
  total: number;
}

export interface BackendSearchRecords {
  record: BackendRecord;
  query_score: number;
}

type BackendFilterAndSortScope = {
  entity: "suggestion" | "record" | "metadata" | "response";
  question?: string;
  property?: string;
  metadata_property?: string;
};

interface AndFilterBackendSearchQuery {
  type: "terms" | "range";
  scope: BackendFilterAndSortScope;
  values?: string[];
  ge?: number;
  le?: number;
}

export type BackendSimilaritySearchOrder = "most_similar" | "least_similar";

export interface BackendSort {
  scope: BackendFilterAndSortScope;
  order: "asc" | "desc";
}

export interface BackendAdvanceSearchQuery {
  query: {
    vector?: {
      name: string;
      record_id: string;
      max_results: number;
      order: BackendSimilaritySearchOrder;
    };
    text?: {
      q: string;
      field?: string;
    };
  };
  filters: {
    and: AndFilterBackendSearchQuery[];
  };
  sort?: BackendSort[];
}

export interface BackendResponseBulkRequest {
  items: {
    status: BackendRecordStatus;
    values: BackendAnswerCombinations;
    record_id: string;
  }[];
}

export interface BackendResponseBulkResponse {
  items: {
    item: BackendResponseResponse & { record_id: string };
    error: {
      detail?: string;
    };
  }[];
}
