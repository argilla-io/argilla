import { CORRESPONDING_FIELD_COMPONENT_TYPE_FROM_API } from "@/components/feedback-task/feedbackTask.properties";

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
