import { isEqual, cloneDeep } from "lodash";
import { COMPONENT_TYPE } from "@/components/feedback-task/feedbackTask.properties";

export const CORRESPONDING_QUESTION_COMPONENT_TYPE_FROM_API = {
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
  private suggestion: any;

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

  public get hasSuggestion(): boolean {
    return !!this.suggestion;
  }

  public get matchSuggestion(): boolean {
    if (this.hasSuggestion) {
      return isEqual(this.options, this.suggestedAnswer);
    }

    return false;
  }

  clearAnswer() {
    this.options = this.createEmptyAnswers();
  }

  answerQuestionWithResponse(response: any) {
    this.options = this.completeQuestionAnswered(response);
  }

  private suggestedAnswer: any;
  answerQuestionWithSuggestion(suggestion: any) {
    this.suggestion = suggestion;
    this.options = this.createEmptyAnswers(suggestion);
    this.suggestedAnswer = cloneDeep(this.options);
  }

  private createEmptyAnswers(suggestion: any = undefined) {
    if (this.isTextType) {
      return suggestion ? [{ ...suggestion }] : this.initialOptions;
    }

    if (this.isMultiLabelType) {
      return this.initialOptions.map((option) => {
        return {
          ...option,
          is_selected: suggestion?.value.includes(option.value),
        };
      });
    }

    if (this.isRatingType || this.isSingleLabelType) {
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
