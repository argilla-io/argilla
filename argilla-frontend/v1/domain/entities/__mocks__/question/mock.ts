import { Question } from "../../question/Question";

export const createTextQuestionMocked = () => {
  return new Question(
    "FAKE_ID",
    "FAKE_NAME",
    "FAKE_DESCRIPTION",
    "FAKE_DATASET_ID",
    "FAKE_ TITLE",
    false,
    {
      type: "label_selection",
      options: [
        {
          value: "positive",
          text: "Positive",
          description: "Texts with a positive intent",
        },

        {
          value: "nostalgic",
          text: "Nostalgic",
          description: "Texts expressing nostalgia",
        },
        {
          value: "sympathetic",
          text: "Sympathetic",
          description: "Texts expressing sympathy",
        },
      ],
      visible_options: 5,
      use_markdown: true,
    }
  );
};

export const createLabelQuestionMocked = (settings: Object) => {
  return new Question(
    "FAKE_ID",
    "FAKE_NAME",
    "FAKE_DESCRIPTION",
    "FAKE_DATASET_ID",
    "FAKE_ TITLE",
    false,
    {
      type: "label_selection",
      options: [
        {
          value: "positive",
          text: "Positive",
          description: "Texts with a positive intent",
        },

        {
          value: "nostalgic",
          text: "Nostalgic",
          description: "Texts expressing nostalgia",
        },
        {
          value: "sympathetic",
          text: "Sympathetic",
          description: "Texts expressing sympathy",
        },
      ],
      visible_options: 5,
      ...settings,
    }
  );
};
