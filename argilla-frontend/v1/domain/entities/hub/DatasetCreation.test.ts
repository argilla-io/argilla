import { DatasetCreationBuilder } from "./DatasetCreationBuilder";

const datasetInfo = {
  default: {
    description: "",
    citation: "",
    homepage: "",
    license: "",
    features: {
      text_field: {
        dtype: "string",
        _type: "Value",
      },
      image_field: {
        dtype: "string",
        _type: "Image",
      },
      label_question: {
        names: ["positive", "negative"],
        _type: "ClassLabel",
      },
      chat_field: [
        {
          content: {
            dtype: "string",
            _type: "Value",
          },
          role: {
            dtype: "string",
            _type: "Value",
          },
        },
      ],
      metadata: {
        dtype: "int32",
        _type: "Value",
      },
    },
    builder_name: "parquet",
    dataset_name: "duorc",
    config_name: "SelfRC",
    version: {
      version_str: "0.0.0",
      major: 0,
      minor: 0,
      patch: 0,
    },
    splits: {
      train: {
        name: "train",
        num_bytes: 248966361,
        num_examples: 60721,
        dataset_name: null,
      },
      validation: {
        name: "validation",
        num_bytes: 56359392,
        num_examples: 12961,
        dataset_name: null,
      },
      test: {
        name: "test",
        num_bytes: 51022318,
        num_examples: 12559,
        dataset_name: null,
      },
    },
    download_size: 21001846,
    dataset_size: 356348071,
  },
};

describe("DatasetCreation", () => {
  describe("build should", () => {
    it("create text field", () => {
      const builder = new DatasetCreationBuilder("FAKE", datasetInfo);

      const datasetCreation = builder.build();

      const firstField = datasetCreation.fields[0];

      expect(firstField.name).toBe("text_field");
      expect(firstField.type.isTextType).toBeTruthy();
      expect(firstField.required).toBeFalsy();
    });

    it("create image field", () => {
      const builder = new DatasetCreationBuilder("FAKE", datasetInfo);

      const datasetCreation = builder.build();

      const secondField = datasetCreation.fields[1];

      expect(secondField.name).toBe("image_field");
      expect(secondField.type.isImageType).toBeTruthy();
      expect(secondField.required).toBeFalsy();
    });

    it("create label question", () => {
      const builder = new DatasetCreationBuilder("FAKE", datasetInfo);

      const datasetCreation = builder.build();

      const labelQuestion = datasetCreation.questions[0];

      expect(labelQuestion.name).toBe("label_question");
      expect(labelQuestion.type.isSingleLabelType).toBeTruthy();
      expect(labelQuestion.required).toBeTruthy();
      expect(labelQuestion.options).toEqual(["positive", "negative"]);
    });

    it("create a required field if the dataset has just one field", () => {
      const datasetInfoWithOneField = {
        default: {
          ...datasetInfo.default,
          features: {
            text_field: {
              dtype: "string",
              _type: "Value",
            },
          },
        },
      };

      const builder = new DatasetCreationBuilder(
        "FAKE",
        datasetInfoWithOneField
      );

      const datasetCreation = builder.build();

      const field = datasetCreation.fields[0];

      expect(field.name).toBe("text_field");
      expect(field.type.isTextType).toBeTruthy();
      expect(field.required).toBeTruthy();
      expect(datasetCreation.fields.length).toBe(1);
    });

    it("create a required question if the dataset has just one field", () => {
      const datasetInfoWithOneQuestion = {
        default: {
          ...datasetInfo.default,
          features: {
            label_question: {
              names: ["positive", "negative"],
              _type: "ClassLabel",
            },
          },
        },
      };

      const builder = new DatasetCreationBuilder(
        "FAKE",
        datasetInfoWithOneQuestion
      );

      const datasetCreation = builder.build();

      const question = datasetCreation.questions[0];

      expect(question.name).toBe("label_question");
      expect(question.type.isSingleLabelType).toBeTruthy();
      expect(question.required).toBeTruthy();
      expect(datasetCreation.questions.length).toBe(1);
    });

    it("create a chat field", () => {
      const builder = new DatasetCreationBuilder("FAKE", datasetInfo);

      const datasetCreation = builder.build();

      const chatField = datasetCreation.fields[2];

      expect(chatField.name).toBe("chat_field");
      expect(chatField.type.isChatType).toBeTruthy();
      expect(chatField.required).toBeFalsy();
    });

    it("get no mapped feature", () => {
      const builder = new DatasetCreationBuilder("FAKE", {
        default: {
          ...datasetInfo.default,
          features: {
            no_mapped: {
              dtype: "NO",
              _type: "NO",
            },
          },
        },
      });

      const datasetCreation = builder.build();

      expect(
        datasetCreation.fields.filter((f) => f.type.value === "no mapping")
          .length
      ).toBe(1);
    });

    it("create metadata", () => {
      const builder = new DatasetCreationBuilder("FAKE", datasetInfo);

      const datasetCreation = builder.build();

      const metadata = datasetCreation.metadata[0];

      expect(metadata.name).toBe("metadata");
      expect(metadata.title).toBe("metadata");
    });
  });

  describe("addQuestions should", () => {
    it("add single label", () => {
      const datasetInfoWithNoQuestions = {
        default: {
          ...datasetInfo.default,
          features: {},
        },
      };
      const builder = new DatasetCreationBuilder(
        "FAKE",
        datasetInfoWithNoQuestions
      );

      const datasetCreation = builder.build();

      datasetCreation.selectedSubset.addQuestion("First", {
        type: "label_selection",
      });

      const firstQuestion = datasetCreation.questions[0];
      expect(firstQuestion.name).toBe("First");
      expect(firstQuestion.type.isSingleLabelType).toBeTruthy();
      expect(firstQuestion.options).toEqual([
        {
          id: "1",
          text: "positive",
          value: "positive",
        },
        {
          id: "2",
          text: "negative",
          value: "negative",
        },
        {
          id: "3",
          text: "neutral",
          value: "neutral",
        },
      ]);
    });

    it("add ranking question", () => {
      const datasetInfoWithNoQuestions = {
        default: {
          ...datasetInfo.default,
          features: {},
        },
      };
      const builder = new DatasetCreationBuilder(
        "FAKE",
        datasetInfoWithNoQuestions
      );

      const datasetCreation = builder.build();

      datasetCreation.selectedSubset.addQuestion("First", {
        type: "ranking",
      });

      const firstQuestion = datasetCreation.questions[0];
      expect(firstQuestion.name).toBe("First");
      expect(firstQuestion.type.isRankingType).toBeTruthy();
      expect(firstQuestion.options).toEqual([
        {
          value: "option1",
          text: "Option 1",
        },
        {
          value: "option2",
          text: "Option 2",
        },
      ]);
    });
  });
});
