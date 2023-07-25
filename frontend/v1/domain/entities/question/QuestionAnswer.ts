import { Answer, RankingAnswer } from "../IAnswer";
import { Suggestion } from "./Suggestion";

export type QuestionType =
  | "text"
  | "rating"
  | "ranking"
  | "label_selection"
  | "multi_label_selection";
export abstract class QuestionAnswer {
  constructor(
    public readonly type: QuestionType,
    public readonly value: unknown
  ) {}

  abstract complete(answer: Answer);
  abstract clear();
  abstract get isValid(): boolean;
  get hasValidValues(): boolean {
    return true;
  }

  abstract get valuesAnswered();

  abstract matchSuggestion(suggestion: Suggestion): boolean;
}
export class TextQuestionAnswer extends QuestionAnswer {
  constructor(public readonly type: QuestionType, public value: string) {
    super(type, value);
  }

  complete(answer: Answer) {
    this.value = answer.value as string;
  }

  clear() {
    this.value = "";
  }

  get isValid(): boolean {
    return this.value !== "";
  }

  get valuesAnswered() {
    return this.value;
  }

  matchSuggestion(suggestion: Suggestion): boolean {
    return this.valuesAnswered === suggestion.suggestedAnswer;
  }
}
type SingleLabelValue = {
  id: string;
  text: string;
  value: string;
  description: string;
  isSelected: boolean;
};
export class SingleLabelQuestionAnswer extends QuestionAnswer {
  public readonly values: SingleLabelValue[];

  constructor(
    public readonly type: QuestionType,
    questionName: string,
    value: SingleLabelValue[]
  ) {
    super(type, value);
    this.values = value.map((label) => ({
      ...label,
      id: `${questionName}_${label.value}`,
      isSelected: false,
    }));
  }

  complete(answer: Answer) {
    this.values.forEach((value) => {
      value.isSelected = value.value === answer.value;
    });
  }

  clear() {
    this.values
      .filter((label) => label.isSelected)
      .forEach((label) => {
        label.isSelected = false;
      });
  }

  get isValid(): boolean {
    return this.values.some((label) => label.isSelected);
  }

  get valuesAnswered(): string {
    return this.values.filter((label) => label.isSelected)[0]?.value;
  }

  matchSuggestion(suggestion: Suggestion): boolean {
    return this.valuesAnswered === suggestion.suggestedAnswer;
  }
}
type MultiLabelValue = {
  id: string;
  text: string;
  value: string;
  description: string;
  isSelected: boolean;
};
export class MultiLabelQuestionAnswer extends QuestionAnswer {
  public readonly values: MultiLabelValue[];

  constructor(
    public readonly type: QuestionType,
    questionName: string,
    value: MultiLabelValue[]
  ) {
    super(type, value);
    this.values = value.map((label) => ({
      ...label,
      id: `${questionName}_${label.value}`,
      isSelected: false,
    }));
  }

  complete(answer: Answer) {
    const answerValues = answer.value as string[];
    this.values.forEach((label) => {
      label.isSelected = answerValues.includes(label.value);
    });
  }

  clear() {
    this.values
      .filter((label) => label.isSelected)
      .forEach((label) => {
        label.isSelected = false;
      });
  }

  get isValid(): boolean {
    return this.values.some((label) => label.isSelected);
  }

  get valuesAnswered(): string[] {
    return this.values
      .filter((label) => label.isSelected)
      .map((label) => label.value);
  }

  matchSuggestion(suggestion: Suggestion): boolean {
    const valuesSuggested = suggestion.suggestedAnswer as string[];

    const equal =
      valuesSuggested.every((answered) =>
        this.valuesAnswered.includes(answered)
      ) && valuesSuggested.length === this.valuesAnswered.length;

    return equal;
  }
}
type RatingValue = {
  id: string;
  value: number;
  isSelected: boolean;
};
export class RatingLabelQuestionAnswer extends QuestionAnswer {
  public readonly values: RatingValue[];

  constructor(
    public readonly type: QuestionType,
    questionName: string,
    value: RatingValue[]
  ) {
    super(type, value);
    this.values = value.map((rating) => ({
      id: `${questionName}_${rating.value}`,
      value: rating.value,
      isSelected: false,
    }));
  }

  complete(answer: Answer) {
    this.values.forEach((rating) => {
      rating.isSelected = rating.value === answer.value;
    });
  }

  clear() {
    this.values
      .filter((label) => label.isSelected)
      .forEach((rating) => {
        rating.isSelected = false;
      });
  }

  get isValid(): boolean {
    return this.values.some((value) => value.isSelected);
  }

  get valuesAnswered(): number {
    return this.values.filter((rating) => rating.isSelected)[0]?.value;
  }

  matchSuggestion(suggestion: Suggestion): boolean {
    return this.valuesAnswered === suggestion.suggestedAnswer;
  }
}
type RankingValue = {
  id: string;
  text: string;
  value: string;
  description: string;
  rank?: number;
};
export class RankingQuestionAnswer extends QuestionAnswer {
  public values: RankingValue[];

  constructor(
    public readonly type: QuestionType,
    questionName: string,
    value: RankingValue[]
  ) {
    super(type, value);
    this.values = value.map((ranking) => ({
      ...ranking,
      id: `${questionName}_${ranking.value}`,
      rank: null,
    }));
  }

  complete(answer: Answer) {
    const suggestedAnswers = answer.value as RankingAnswer[];
    this.values.forEach((ranking) => {
      ranking.rank = suggestedAnswers.find(
        (s) => s.value === ranking.value
      )?.rank;
    });
  }

  clear() {
    this.values.forEach((ranking) => {
      ranking.rank = null;
    });
  }

  get isValid(): boolean {
    return this.values.every((value) => value.rank);
  }

  get hasValidValues(): boolean {
    return (
      !this.values.some((option) => option.rank) ||
      this.values.every((option) => option.rank)
    );
  }

  get valuesAnswered(): RankingValue[] {
    return this.values;
  }

  matchSuggestion(suggestion: Suggestion): boolean {
    const suggestedAnswers = suggestion.suggestedAnswer as RankingAnswer[];
    return suggestedAnswers.every(
      (suggested) =>
        this.values.find((value) => value.value === suggested.value)?.rank ===
        suggested.rank
    );
  }
}
