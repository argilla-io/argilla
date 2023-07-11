import { COMPONENT_TYPE } from "~/components/feedback-task/feedbackTask.properties";

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

  public records: any[] = [];

  addRecords(records: unknown[]) {
    this.records = records;
  }

  getAnswer(recordId: string) {
    return this.questionsWithRecordAnswers(recordId);
  }

  questionsWithRecordAnswers(recordId: string) {
    const record = this.records.find((r) => r.id === recordId);
    return this.questions?.map((question) => {
      const correspondingResponseToQuestion = record.responses.find(
        (recordResponse) => question.name === recordResponse.question_name
      );
      if (correspondingResponseToQuestion) {
        return this.completeQuestionAnswered(
          question,
          correspondingResponseToQuestion
        );
      }

      const suggestion = [
        ...record.suggestions,
        { question_id: "fe94beff-cdd2-4e3b-b19b-3023fbce5258", value: "Hola" },
        {
          question_id: "8919dcf4-882c-4dd8-b0f5-9483df80beb4",
          value: "positive",
        },
      ].find((s) => s.question_id === question.id);

      return this.createEmptyResponse(question, suggestion);
    });
  }

  private completeQuestionAnswered(
    question: Question,
    correspondingResponseToQuestion: any
  ) {
    let formattedOptions = [];

    switch (question.component_type) {
      case COMPONENT_TYPE.RANKING:
        formattedOptions = correspondingResponseToQuestion.options;
        break;
      case COMPONENT_TYPE.FREE_TEXT:
      case COMPONENT_TYPE.SINGLE_LABEL:
      case COMPONENT_TYPE.MULTI_LABEL:
      case COMPONENT_TYPE.RATING:
        formattedOptions = correspondingResponseToQuestion.options.map(
          (option) => {
            return {
              ...option,
              is_selected: option.is_selected || false,
            };
          }
        );
        break;
      default:
        console.log(`The component ${question.component_type} is unknown`);
    }
    return {
      ...question,
      response_id: correspondingResponseToQuestion.id,
      options: formattedOptions,
    };
  }

  private createEmptyResponse(question: Question, suggestion: any) {
    if (question.component_type === COMPONENT_TYPE.FREE_TEXT && suggestion) {
      return {
        ...question,
        options: [{ ...suggestion }],
      };
    }

    if (
      question.component_type === COMPONENT_TYPE.RATING ||
      question.component_type === COMPONENT_TYPE.SINGLE_LABEL ||
      question.component_type === COMPONENT_TYPE.MULTI_LABEL
    ) {
      const formattedOptions = question.options.map((option) => {
        return { ...option, is_selected: option.value === suggestion?.value };
      });
      return { ...question, options: formattedOptions, response_id: null };
    }

    if (question.component_type === COMPONENT_TYPE.RANKING) {
      const formattedOptions = question.options.map((option) => {
        return { ...option, rank: null };
      });
      return { ...question, options: formattedOptions, response_id: null };
    }

    return { ...question, response_id: null };
  }
}
