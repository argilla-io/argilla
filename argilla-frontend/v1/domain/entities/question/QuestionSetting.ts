import { QuestionType } from "./QuestionType";

export interface QuestionPrototype {
  type:
    | "label_selection"
    | "multi_label_selection"
    | "ranking"
    | "text"
    | "span"
    | "rating";
  use_markdown?: boolean;
  visible_options?: number;
  options?: any[];
  options_order?: "natural" | "suggestion";
  allow_overlapping?: boolean;
  allow_character_annotation?: boolean;
  field?: string;
}

export class QuestionSetting {
  type: QuestionType;
  use_markdown: boolean;
  visible_options: number;
  allow_overlapping: boolean;
  allow_character_annotation: boolean;
  field: string;
  options: any;
  options_order: "natural" | "suggestion";

  constructor(private readonly settings: QuestionPrototype) {
    this.type = QuestionType.from(settings.type);

    this.use_markdown = settings.use_markdown;
    this.visible_options = settings.visible_options;
    this.options = settings.options;
    this.options_order = settings.options_order;
    this.allow_overlapping = settings.allow_overlapping;
    this.allow_character_annotation = settings.allow_character_annotation;
    this.field = settings.field;
  }

  get suggestionFirst() {
    if (!this.options_order) return undefined;

    return this.options_order === "suggestion";
  }

  set suggestionFirst(value: boolean) {
    this.options_order = value ? "suggestion" : "natural";
  }

  get shouldShowVisibleOptions() {
    return this.options?.length > 3 && "visible_options" in this.settings;
  }

  isEqual(setting: QuestionSetting) {
    return (
      this.use_markdown === setting.use_markdown &&
      this.visible_options === setting.visible_options &&
      this.options_order === setting.options_order &&
      JSON.stringify(this.options) === JSON.stringify(setting.options)
    );
  }
}
