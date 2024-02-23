export type RankingAnswer = { value: string; rank: number };

type Field = string;
export type SpanAnswer = Record<
  Field,
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
