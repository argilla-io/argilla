import {
  Answer,
  AnswerCombinations,
  RankingAnswer,
  SpanAnswer,
} from "../IAnswer";
import { QuestionType } from "./QuestionType";

type AnswerValue = string | number | RankingAnswer | SpanAnswer;

interface SuggestionValue {
  value: AnswerValue;
  score: number;
  agent: string;
}

export class Suggestion implements Answer {
  constructor(
    private readonly id: string,
    public readonly questionId: string,
    private readonly questionType: QuestionType,
    private readonly suggestedAnswer: AnswerCombinations,
    private readonly score: number | number[],
    private readonly agent: string
  ) {}

  get value() {
    return this.suggestedAnswer;
  }

  isSuggested(answer: AnswerValue) {
    return !!this.getSuggestion(answer);
  }

  getSuggestion(answer: AnswerValue): SuggestionValue | undefined {
    if (
      this.questionType.isSingleLabelType ||
      this.questionType.isTextType ||
      this.questionType.isRatingType
    ) {
      if (this.value === answer) {
        return {
          value: answer,
          score: this.score as number,
          agent: this.agent,
        };
      }
    }

    if (this.questionType.isMultiLabelType) {
      const multiLabel = this.value as string[];
      const answerValue = answer as string;

      if (multiLabel.includes(answerValue)) {
        const indexOf = multiLabel.indexOf(answerValue);

        return {
          value: answer,
          score: this.score[indexOf],
          agent: this.agent,
        };
      }
    }

    if (this.questionType.isSpanType) {
      const span = answer as SpanAnswer;
      const suggestions = this.value as SpanAnswer[];

      const spanSuggested = suggestions.find(
        (s) =>
          s.label === span.label && s.start === span.start && s.end === span.end
      );

      if (spanSuggested) {
        const indexOf = suggestions.indexOf(spanSuggested);

        return {
          value: spanSuggested,
          score: this.score[indexOf],
          agent: this.agent,
        };
      }
    }

    if (this.questionType.isRankingType) {
      const suggestedRanking = this.value as RankingAnswer[];
      const ranking = answer as RankingAnswer;

      const rankingSuggested = suggestedRanking.find(
        (s) => s.value === ranking.value
      );

      if (rankingSuggested) {
        const indexOf = suggestedRanking.indexOf(rankingSuggested);
        return {
          value: rankingSuggested,
          score: this.score[indexOf],
          agent: this.agent,
        };
      }
    }
  }
}
