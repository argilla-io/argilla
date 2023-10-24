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
}

export interface BackedRecords {
  records: BackedRecord[];
  total: number;
}

export interface BackendSearchRecords {
  record: BackedRecord;
}

export interface BackendAdvanceSearchQuery {
  query: {
    vector?: {
      name: string;
      record_id: string;
      max_results: number;
      order: "most_similar" | "least_similar";
    };
    text?: {
      q: string;
    };
  };
}
