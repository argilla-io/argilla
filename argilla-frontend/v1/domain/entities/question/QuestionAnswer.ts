import { Answer, RankingAnswer, SpanAnswer } from "../IAnswer";
import { QuestionType } from "./QuestionType";

export abstract class QuestionAnswer {
  private _answer: Answer;
  constructor(public readonly type: QuestionType) {}

  get isPartiallyValid(): boolean {
    return false;
  }

  get hasValidValues(): boolean {
    return true;
  }

  get answer() {
    return this._answer;
  }

  response(answer: Answer) {
    this._answer = answer;
    this.fill(this._answer);
  }

  isEqual(answer: QuestionAnswer) {
    const isEqual =
      JSON.stringify(this.valuesAnswered) ===
      JSON.stringify(answer.valuesAnswered);

    return isEqual;
  }

  protected abstract fill(answer: Answer);
  abstract clear();
  abstract get isValid(): boolean;
  abstract get valuesAnswered();
}
export class TextQuestionAnswer extends QuestionAnswer {
  public originalValue: string;
  constructor(public readonly type: QuestionType, public value: string) {
    super(type);
  }

  protected fill(answer: Answer) {
    this.originalValue = this.value = answer.value as string;
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
}

type Option = {
  id: string;
  value: string;
  text: string;
  color: string;
  isSelected: boolean;
};

export class SpanQuestionAnswer extends QuestionAnswer {
  public readonly options: Option[] = [];
  public values: SpanAnswer[] = [];

  constructor(
    public readonly type: QuestionType,
    questionName: string,
    options: Omit<Option, "isSelected" | "id">[]
  ) {
    super(type);

    const makeSafeForCSS = (str: string) => {
      return str.replace(/[^a-z0-9]/g, (s) => {
        const c = s.charCodeAt(0);
        if (c === 32) return "-";
        if (c >= 65 && c <= 90) return `-${s.toLowerCase()}`;
        return `-${c.toString(16)}`;
      });
    };

    this.options = options.map((e) => ({
      ...e,
      id: makeSafeForCSS(`${questionName}-${e.value}`),
      isSelected: false,
    }));
    this.clear();
  }

  protected fill(answer: Answer) {
    this.values = answer.value as SpanAnswer[];
  }

  clear() {
    this.values = [];
  }

  get isValid(): boolean {
    return true;
  }

  get valuesAnswered(): SpanAnswer[] {
    return this.values.map((value) => ({
      start: value.start,
      end: value.end,
      label: value.label,
    }));
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
    super(type);
    this.values = value.map((label) => ({
      ...label,
      id: `${questionName}_${label.value}`,
      isSelected: false,
    }));
  }

  protected fill(answer: Answer) {
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
    super(type);
    this.values = value.map((label) => ({
      ...label,
      id: `${questionName}_${label.value}`,
      isSelected: false,
    }));
  }

  protected fill(answer: Answer) {
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
    super(type);
    this.values = value.map((rating) => ({
      id: `${questionName}_${rating.value}`,
      value: rating.value,
      isSelected: false,
    }));
  }

  protected fill(answer: Answer) {
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
    super(type);
    this.values = value.map((ranking) => ({
      ...ranking,
      id: `${questionName}_${ranking.value}`,
      rank: null,
    }));
  }

  protected fill(answer: Answer) {
    const value = answer.value as RankingAnswer[];

    this.values.forEach((ranking) => {
      ranking.rank = value.find((s) => s.value === ranking.value)?.rank;
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

  get isPartiallyValid(): boolean {
    return this.values.some((value) => value.rank);
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
}
