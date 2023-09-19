interface RatingSetting {
  type: "rating";
  options: {
    value: number;
  }[];
}
interface TextSetting {
  type: "text";
  use_markdown: boolean;
}
interface RankingSetting {
  type: "ranking";
  options: {
    description?: string;
    text: string;
    value: string;
  }[];
}
interface MultiSelectionSetting {
  type: "multi_label_selection";
  visible_options: number;
  options: {
    description?: string;
    text: string;
    value: string;
  }[];
}
interface SingleSelectionSetting {
  type: "label_selection";
  options: {
    description?: string;
    text: string;
    value: string;
  }[];
}
export interface BackendQuestion {
  id: string;
  description?: string;
  name: string;
  title: string;
  required: boolean;
  settings:
    | TextSetting
    | MultiSelectionSetting
    | SingleSelectionSetting
    | RatingSetting
    | RankingSetting;
}
