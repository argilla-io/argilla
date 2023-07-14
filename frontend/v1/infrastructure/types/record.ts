interface BackendSuggestion {
  id: string;
  question_id: string;
  value: string | string[] | number | { value: string; rank: number }[];
}
export type BackendResponseStatus = "submitted" | "pending" | "discarded";

export type BackendRankingAnswer = { value: string; rank: number };
export type BackendAnswerCombinations =
  | string
  | string[]
  | number
  | BackendRankingAnswer[];
export interface BackendResponse {
  id: string;
  status: BackendResponseStatus;
  values: BackendAnswerCombinations;
}
export interface BackedRecord {
  id: string;
  suggestions: BackendSuggestion[];
  responses: BackendResponse[];
  fields: { [key: string]: string };
}
export interface BackedRecords {
  records: BackedRecord[];
  total: number;
}
