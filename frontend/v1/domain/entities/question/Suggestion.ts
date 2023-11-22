import { Answer, AnswerCombinations } from "../IAnswer";

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
}
