import { Color } from "../color/Color";

const STATUS = {
  pending: "hsl(35, 90%, 39%)",
  discarded: "hsl(0, 2%, 76%)",
  submitted: "hsl(227, 56%, 52%)",
  draft: "hsl(188, 92%, 39%)",
};

type Status = keyof typeof STATUS;

export class RecordStatus extends String {
  public readonly color: Color;
  private constructor(public readonly name: Status, color: string) {
    super(name);

    this.color = Color.from(color);
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
