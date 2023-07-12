import {
  COMPONENT_TYPE,
  CORRESPONDING_FIELD_COMPONENT_TYPE_FROM_API,
} from "~/components/feedback-task/feedbackTask.properties";

const CORRESPONDING_QUESTION_COMPONENT_TYPE_FROM_API = {
  text: COMPONENT_TYPE.FREE_TEXT,
  rating: COMPONENT_TYPE.RATING,
  ranking: COMPONENT_TYPE.RANKING,
  label_selection: COMPONENT_TYPE.SINGLE_LABEL,
  multi_label_selection: COMPONENT_TYPE.MULTI_LABEL,
};

export class Question {
  public readonly question: string;
  public readonly component_type: string;
  public readonly dataset_id: string;
  public readonly is_required: boolean;
  public readonly options: any;
  public readonly placeholder: string; // IT'S THING RELATED TO COMPONENT; REMOVE IT

  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly description: string,
    public readonly datasetId: string,
    public readonly title: string,
    public readonly isRequired: boolean,
    public readonly settings: any
  ) {
    this.component_type =
      CORRESPONDING_QUESTION_COMPONENT_TYPE_FROM_API[this.questionType];
    this.dataset_id = this.datasetId;
    this.is_required = this.isRequired;
    this.question = this.title;
    this.placeholder = this.settings?.placeholder ?? null;
    this.options = this.formatOptionsFromQuestionApi(
      this.settings.options,
      this.name
    );
  }

  public get questionType(): string {
    return this.settings.type.toLowerCase();
  }

  private formatOptionsFromQuestionApi(options, questionName) {
    if (options) {
      return options?.map((option) => {
        const optionText = option.text ?? option.value;
        const paramObject = {
          value: option.value,
          text: optionText,
          prefixId: questionName,
          suffixId: option.value,
        };

        return this.factoryOption(paramObject);
      });
    }

    return [
      this.factoryOption({
        value: "",
        prefixId: questionName,
      }),
    ];
  }

  private factoryOption({ value = null, text = "", prefixId, suffixId }: any) {
    return {
      id: `${prefixId}${suffixId ? `_${suffixId}` : ""}`,
      value,
      text,
    };
  }
}

export class Field {
  public readonly component_type: string;
  public readonly dataset_id: string;
  public readonly is_required: boolean;

  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly title: string,
    public readonly datasetId: string,
    public readonly required: boolean,
    public readonly settings: any
  ) {
    this.dataset_id = this.datasetId;
    this.is_required = this.required;
    this.component_type = this.fieldSetting
      ? CORRESPONDING_FIELD_COMPONENT_TYPE_FROM_API[this.fieldSetting]
      : null;
  }

  private get fieldSetting() {
    return this.settings?.type?.toLowerCase() ?? null;
  }
}

export class Feedback {
  constructor(
    public readonly questions: Question[],
    public readonly fields: Field[]
  ) {}

  public records: any[] = [];

  addRecords(records: unknown[]) {
    this.records = [...this.records, ...records];
  }

  updateResponse(response: any) {
    const record = this.records.find((r) => r.id === response.record_id);

    record.responses = record.responses.map((r) => {
      if (r.id === response.id) return response;

      return r;
    });
  }

  addResponse(response: any) {
    const record = this.records.find((r) => r.id === response.record_id);

    record.responses.push(response);
  }

  clearRecord(recordId: string, status: string) {
    const record = this.records.find((r) => r.id === recordId);

    if (!record) return;

    record.responses = [];
    record.status = status;
  }

  getAnswer(recordId: string, userId: string) {
    return this.questionsWithRecordAnswers(recordId, userId);
  }

  questionsWithRecordAnswers(recordId: string, userId: string) {
    const record = this.records.find((r) => r.id === recordId);
    const response = record?.responses.filter(
      (response) => response.user_id === userId
    )[0];

    return this.questions?.map((question) => {
      const correspondingResponseToQuestion = response?.values[question.name];
      if (correspondingResponseToQuestion) {
        return this.completeQuestionAnswered(
          question,
          correspondingResponseToQuestion
        );
      }

      const suggestion = record.suggestions?.find(
        (s) => s.question_id === question.id
      );

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
        formattedOptions = correspondingResponseToQuestion.value;
        break;

      case COMPONENT_TYPE.FREE_TEXT:
        formattedOptions = [
          { ...question.options, value: correspondingResponseToQuestion.value },
        ];
        break;
      case COMPONENT_TYPE.MULTI_LABEL:
        formattedOptions = question.options.map((option) => {
          return {
            ...option,
            is_selected: correspondingResponseToQuestion.value.includes(
              option.value
            ),
          };
        });
        break;
      case COMPONENT_TYPE.SINGLE_LABEL:
      case COMPONENT_TYPE.RATING:
        formattedOptions = question.options.map((option) => {
          return {
            ...option,
            is_selected: option.value === correspondingResponseToQuestion.value,
          };
        });
        break;
    }
    return {
      ...question,
      response_id: correspondingResponseToQuestion.id,
      options: formattedOptions,
    };
  }

  private createEmptyResponse(question: Question, suggestion: any) {
    if (question.component_type === COMPONENT_TYPE.FREE_TEXT) {
      return {
        ...question,
        options: suggestion ? [{ ...suggestion }] : question.options,
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
