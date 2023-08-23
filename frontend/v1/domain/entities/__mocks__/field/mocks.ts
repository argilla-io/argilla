import { Field } from "../../field/Field";

export const createTextFieldMock = (id: string) => {
  return new Field(id, "NAME", "TITLE", "CONTENT", "DATASET_ID", true, {
    use_markdown: true,
    type: "text",
  });
};
