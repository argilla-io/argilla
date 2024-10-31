import { Color } from "../color/Color";

const STATUS = {
  pending: "var(--fg-status-pending)",
  discarded: "var(--fg-status-discarded)",
  submitted: "var(--fg-status-submitted)",
  draft: "var(--fg-status-draft)",
};

type Status = keyof typeof STATUS;

export class RecordStatus extends String {
  public readonly color: Color;
  private constructor(public readonly name: Status, color: string) {
    super(name);

    const resolvedColor = color.startsWith("var(") ? this.resolveCssVariable(color.slice(4, -1).trim()) : color;
    this.color = Color.from(resolvedColor);
  }

  private resolveCssVariable(varName) {
      return getComputedStyle(document.documentElement).getPropertyValue(varName);
  }
  public static from(name: string): RecordStatus {
    const colorSelected = STATUS[name];

    if (!colorSelected) {
      throw new Error(`Invalid RecordStatus value: ${name}`);
    }

    return new RecordStatus(name as Status, colorSelected);
  }

  public static get pending(): RecordStatus {
    return RecordStatus.from("pending");
  }

  public static get discarded(): RecordStatus {
    return RecordStatus.from("discarded");
  }

  public static get submitted(): RecordStatus {
    return RecordStatus.from("submitted");
  }

  public static get draft(): RecordStatus {
    return RecordStatus.from("draft");
  }
}
