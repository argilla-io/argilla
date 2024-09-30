import { Field } from "../../field/Field";

export const createTextFieldMock = (id: string) => {
  return new Field(
    id,
    "NAME",
    "TITLE",
    "CONTENT",
    true,
    {
      use_markdown: true,
      type: "text",
    },
    {
      fields: {
        NAME: "CONTENT",
      },
    }
  );
};
