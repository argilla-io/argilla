import { Answer, AnswerCombinations } from "../IAnswer";

export class RecordAnswer implements Answer {
  constructor(
    public readonly id: string,
    public status: "submitted" | "pending" | "discarded",
    public readonly value: AnswerCombinations
  ) {}

  discard() {
    this.status = "discarded";
  }

  pending() {
    this.status = "pending";
  }
}
