export class QuestionSetting {
  use_markdown: boolean;
  visible_options: number;
  options: any;
  options_order: "natural" | "suggestion";
  type: string;

  constructor(settings: any) {
    this.type = settings.type;

    this.use_markdown = settings.use_markdown;
    this.visible_options = settings.visible_options;
    this.options = settings.options;
    this.options_order = settings.options_order;
  }

  get suggestionFirst() {
    if (!this.options_order) return undefined;

    return this.options_order === "suggestion";
  }

  set suggestionFirst(value: boolean) {
    this.options_order = value ? "suggestion" : "natural";
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
