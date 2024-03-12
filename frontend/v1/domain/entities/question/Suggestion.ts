import { Answer, AnswerCombinations, SpanAnswer } from "../IAnswer";

export class Suggestion implements Answer {
  constructor(
    public readonly id: string,
    public readonly questionId: string,
    public readonly suggestedAnswer: AnswerCombinations,
    public readonly score: number,
    public readonly agent: string
  ) {}

  get value() {
    return this.suggestedAnswer;
  }

  getSuggestion(span: SpanAnswer) {
    const suggestions = this.value as SpanAnswer[];

    return suggestions.find(
      (s) =>
        s.label === span.label && s.start === span.start && s.end === span.end
    );
  }
}
