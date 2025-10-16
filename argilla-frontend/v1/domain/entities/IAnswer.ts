export type RankingAnswer = { value: string; rank: number };

export type SpanAnswer = {
  start: number;
  end: number;
  label: string;
};

export type ImageAnnotationHole = {
  points: number[][];
  shape_type: string;
  flags?: Record<string, any>;
};

export type ImageAnnotationAnswer = {
  label: string;
  points: number[][];
  shape_type: string;
  group_id?: number;
  flags?: Record<string, any>;
  holes?: ImageAnnotationHole[];
};

export type AnswerCombinations =
  | string
  | string[]
  | number
  | RankingAnswer[]
  | SpanAnswer[]
  | ImageAnnotationAnswer[];

export interface Answer {
  value: AnswerCombinations;
}
