export type RankingAnswer = { value: string; rank: number };
export type AnswerCombinations = string | string[] | number | RankingAnswer[];

export interface Answer {
  value: AnswerCombinations;
}
