import {
  Answer,
  AnswerCombinations,
  RankingAnswer,
  SpanAnswer,
} from "../IAnswer";
import { Question } from "./Question";

export class Suggestion implements Answer {
  constructor(
    public readonly id: string,
    public readonly question: Question,
    public readonly suggestedAnswer: AnswerCombinations,
    public readonly score: number,
    public readonly agent: string
  ) {}

  get value() {
    return this.suggestedAnswer;
  }

  isSuggested(answer: string | number | RankingAnswer | SpanAnswer) {
    return !!this.getSuggestion(answer);
  }

  getSuggestion(answer: string | number | RankingAnswer | SpanAnswer) {
    if (
      this.question.isSingleLabelType ||
      this.question.isTextType ||
      this.question.isRatingType
    ) {
      return this.value === answer;
    }

    if (this.question.isMultiLabelType) {
      const multiLabel = this.value as string[];
      const answerValue = answer as string;

      return multiLabel.includes(answerValue);
    }

    if (this.question.isSpanType) {
      const span = answer as SpanAnswer;
      const suggestions = this.value as SpanAnswer[];

      return suggestions.find(
        (s) =>
          s.label === span.label && s.start === span.start && s.end === span.end
      );
    }

    if (this.question.isRankingType) {
      const suggestedRanking = this.value as RankingAnswer[];
      const ranking = answer as RankingAnswer;

      return suggestedRanking.find((s) => s.value === ranking.value);
    }
  }
}
