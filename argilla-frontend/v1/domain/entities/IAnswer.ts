export type RankingAnswer = { value: string; rank: number };

export type SpanAnswer = {
  start: number;
  end: number;
  label: string;
};

export type AnswerCombinations =
  | string
  | string[]
  | number
  | RankingAnswer[]
  | SpanAnswer[];

export interface Answer {
  value: AnswerCombinations;
}
