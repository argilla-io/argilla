import {
  Answer,
  AnswerCombinations,
  RankingAnswer,
  SpanAnswer,
} from "../IAnswer";
import { QuestionType } from "./QuestionType";

export class Suggestion implements Answer {
  constructor(
    public readonly id: string,
    public readonly questionId: string,
    public readonly questionType: QuestionType,
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
      this.questionType.isSingleLabelType ||
      this.questionType.isTextType ||
      this.questionType.isRatingType
    ) {
      return this.value === answer;
    }

    if (this.questionType.isMultiLabelType) {
      const multiLabel = this.value as string[];
      const answerValue = answer as string;

      return multiLabel.includes(answerValue);
    }

    if (this.questionType.isSpanType) {
      const span = answer as SpanAnswer;
      const suggestions = this.value as SpanAnswer[];

      return suggestions.find(
        (s) =>
          s.label === span.label && s.start === span.start && s.end === span.end
      );
    }

    if (this.questionType.isRankingType) {
      const suggestedRanking = this.value as RankingAnswer[];
      const ranking = answer as RankingAnswer;

      return suggestedRanking.find((s) => s.value === ranking.value);
    }
  }
}
