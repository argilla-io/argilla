import {
  Answer,
  AnswerCombinations,
  RankingAnswer,
  SpanAnswer,
} from "../IAnswer";
import { QuestionType } from "./QuestionType";

type AnswerValue = string | number | RankingAnswer | SpanAnswer;

class SuggestionScore extends Number {
  private constructor(value: number) {
    super(value);
  }

  get fixed() {
    return this.toFixed(1);
  }

  static from(value: number) {
    return new SuggestionScore(value);
  }
}

export class SuggestionValue {
  public readonly score: SuggestionScore;
  constructor(
    public readonly value: AnswerValue,
    score: number,
    public readonly agent: string
  ) {
    this.score = score ? SuggestionScore.from(score) : undefined;
  }
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
        return new SuggestionValue(answer, this.score as number, this.agent);
      }
    }

    if (this.questionType.isMultiLabelType) {
      const multiLabel = this.value as string[];
      const answerValue = answer as string;

      if (multiLabel.includes(answerValue)) {
        const indexOf = multiLabel.indexOf(answerValue);

        return new SuggestionValue(
          answerValue,
          this.score?.[indexOf],
          this.agent
        );
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

        return new SuggestionValue(
          spanSuggested,
          this.score?.[indexOf],
          this.agent
        );
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

        return new SuggestionValue(
          rankingSuggested,
          this.score?.[indexOf],
          this.agent
        );
      }
    }
  }
}
