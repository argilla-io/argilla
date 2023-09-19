import { Answer, AnswerCombinations } from "../IAnswer";

export class Suggestion implements Answer {
  constructor(
    public readonly id: string,
    public readonly questionId: string,
    public readonly suggestedAnswer: AnswerCombinations
  ) {}

  get value() {
    return this.suggestedAnswer;
  }
}
