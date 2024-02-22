export type RankingAnswer = { value: string; rank: number };

// The key represents the entity name.
export type SpanAnswer = Record<
  string,
  { from: number; to: number; entity: string }[]
>;
export type AnswerCombinations =
  | string
  | string[]
  | number
  | RankingAnswer[]
  | SpanAnswer;

export interface Answer {
  value: AnswerCombinations;
}
