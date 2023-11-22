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
}
export type BackendRecordStatus = "submitted" | "discarded" | "draft";

export interface BackendResponse {
  id: string;
  status: BackendRecordStatus;
  values: BackendAnswerCombinations;
  updated_at: string;
}

export interface BackedRecord {
  id: string;
  suggestions: BackendSuggestion[];
  responses: BackendResponse[];
  fields: { [key: string]: string };
  updated_at: string;
  query_score: number;
}

export interface BackedRecords {
  records: BackedRecord[];
  total: number;
}

export interface BackendSearchRecords {
  record: BackedRecord;
  query_score: number;
}

interface AndFilterBackendSearchQuery {
  type: "terms" | "range";
  scope: {
    entity: "response" | "suggestion" | "metadata";
    question?: string;
    property?: "values" | "score" | "agent";
    metadata_property?: string;
  };
  values?: string[];
  gte?: number;
  lte?: number;
}

export type BackendSimilaritySearchOrder = "most_similar" | "least_similar";

export interface BackendSort {
  scope: {
    entity: "suggestion" | "record" | "metadata";
    question?: string;
    property?: string;
  };
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
    };
  };
  filters: {
    and: AndFilterBackendSearchQuery[];
  };
  sort: BackendSort[];
}
