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

type QuestionType =
  | "text"
  | "rating"
  | "ranking"
  | "label_selection"
  | "multi_label_selection";

export class Question {
  public readonly question: string;
  public readonly component_type: string;
  public readonly dataset_id: string;
  public readonly is_required: boolean;
  public readonly initialOptions: any;
  // OLD NAME WAS OPTION
  public options: any;
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
      CORRESPONDING_QUESTION_COMPONENT_TYPE_FROM_API[this.type];
    this.dataset_id = this.datasetId;
    this.is_required = this.isRequired;
    this.question = this.title;
    this.placeholder = this.settings?.placeholder ?? null;
    this.initialOptions = this.formatOptionsFromQuestionApi(
      this.settings.options,
      this.name
    );
  }

  public get type(): QuestionType {
    return this.settings.type.toLowerCase();
  }

  clearAnswer() {
    this.options = this.createEmptyAnswers();
  }

  answerQuestionWithResponse(response: any) {
    this.options = this.completeQuestionAnswered(response);
  }

  answerQuestionWithSuggestion(suggestion: any) {
    this.options = this.createEmptyAnswers(suggestion);
  }

  private createEmptyAnswers(suggestion: any = undefined) {
    if (this.isTextType) {
      return suggestion ? [{ ...suggestion }] : this.initialOptions;
    }

    if (this.isRatingType || this.isSingleLabelType || this.isMultiLabelType) {
      return this.initialOptions.map((option) => {
        return { ...option, is_selected: option.value === suggestion?.value };
      });
    }

    if (this.isRankingType) {
      return this.initialOptions.map((option) => {
        return {
          ...option,
          rank: suggestion?.value.find((s) => s.value === option.value)?.rank,
        };
      });
    }
  }

  public get isRankingType(): boolean {
    return this.type === "ranking";
  }

  public get isMultiLabelType(): boolean {
    return this.type === "multi_label_selection";
  }

  public get isSingleLabelType(): boolean {
    return this.type === "label_selection";
  }

  public get isTextType(): boolean {
    return this.type === "text";
  }

  public get isRatingType(): boolean {
    return this.type === "rating";
  }

  private completeQuestionAnswered(response: any) {
    if (this.isRankingType) {
      return response.value;
    }

    if (this.isTextType) {
      return [{ ...this.initialOptions, value: response.value }];
    }

    if (this.isMultiLabelType) {
      return this.initialOptions.map((option) => {
        return {
          ...option,
          is_selected: response.value.includes(option.value),
        };
      });
    }

    if (this.isSingleLabelType || this.isRatingType) {
      return this.initialOptions.map((option) => {
        return {
          ...option,
          is_selected: option.value === response.value,
        };
      });
    }
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
    public readonly questions: Question[] = [],
    public readonly fields: Field[] = []
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

  checkIfQuestionHasSuggestion(recordId: string, questionId: string) {
    const record = this.records.find((r) => r.id === recordId);
    return record.suggestions?.some((s) => s.question_id === questionId);
  }

  getAnswer(recordId: string, userId: string) {
    return this.questionsWithRecordAnswers(recordId, userId);
  }

  getAnswerWithNoSuggestions() {
    this.questions?.forEach((question) => {
      question.clearAnswer();
    });

    return this.questions;
  }

  questionsWithRecordAnswers(recordId: string, userId: string) {
    const record = this.records.find((r) => r.id === recordId);

    const response = record?.responses.filter(
      (response) => response.user_id === userId
    )[0];

    return this.questions.map((question) => {
      const userAnswer = response?.values[question.name];
      if (userAnswer) {
        question.answerQuestionWithResponse(userAnswer);
      } else {
        const suggestion = record.suggestions?.find(
          (s) => s.question_id === question.id
        );

        question.answerQuestionWithSuggestion(suggestion);
      }

      return question;
    });
  }
}
