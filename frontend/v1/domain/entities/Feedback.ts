export class Question {
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly description: string,
    public readonly dataset_id: string,
    public readonly question: string,
    public readonly order: number,
    public readonly is_required: boolean,
    public readonly settings: any,
    public readonly options: any,
    public readonly component_type: string,
    public readonly placeholder: string
  ) {}

  public get questionType(): string {
    return this.settings.type.toLowerCase();
  }
}

export class Field {
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly title: string,
    public readonly dataset_id: string,
    public readonly order: number,
    public readonly required: boolean,
    public readonly settings: any,
    public readonly component_type: string
  ) {}
}

export class Feedback {
  constructor(
    public readonly questions: Question[],
    public readonly fields: Field[]
  ) {}
}
