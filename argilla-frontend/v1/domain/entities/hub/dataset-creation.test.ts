import { DatasetCreationBuilder } from "./dataset-creation";

const datasetInfo = {
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
};

describe("DatasetCreation", () => {
  describe("build should", () => {
    it("create text field", () => {
      const builder = new DatasetCreationBuilder(datasetInfo);

      const datasetCreation = builder.build();

      const firstField = datasetCreation.fields[0];

      expect(firstField.name).toBe("text_field");
      expect(firstField.isTextType).toBeTruthy();
      expect(firstField.required).toBeFalsy();
    });

    it("create image field", () => {
      const builder = new DatasetCreationBuilder(datasetInfo);

      const datasetCreation = builder.build();

      const secondField = datasetCreation.fields[1];

      expect(secondField.name).toBe("image_field");
      expect(secondField.isImageType).toBeTruthy();
      expect(secondField.required).toBeFalsy();
    });

    it("create label question", () => {
      const builder = new DatasetCreationBuilder(datasetInfo);

      const datasetCreation = builder.build();

      const labelQuestion = datasetCreation.questions[0];

      expect(labelQuestion.name).toBe("label_question");
      expect(labelQuestion.type.isSingleLabelType).toBeTruthy();
      expect(labelQuestion.required).toBeFalsy();
      expect(labelQuestion.options).toEqual(["positive", "negative"]);
    });

    it("create a text field if the dataset no has fields", () => {
      const datasetInfoWithoutFields = {
        ...datasetInfo,
        features: {},
      };

      const builder = new DatasetCreationBuilder(datasetInfoWithoutFields);

      const datasetCreation = builder.build();

      const field = datasetCreation.fields[0];

      expect(field.name).toBe("prompt");
      expect(field.isTextType).toBeTruthy();
      expect(field.required).toBeTruthy();
      expect(datasetCreation.fields.length).toBe(1);
    });

    it("create a required field if the dataset has just one field", () => {
      const datasetInfoWithOneField = {
        ...datasetInfo,
        features: {
          text_field: {
            dtype: "string",
            _type: "Value",
          },
        },
      };

      const builder = new DatasetCreationBuilder(datasetInfoWithOneField);

      const datasetCreation = builder.build();

      const field = datasetCreation.fields[0];

      expect(field.name).toBe("text_field");
      expect(field.isTextType).toBeTruthy();
      expect(field.required).toBeTruthy();
      expect(datasetCreation.fields.length).toBe(1);
    });

    it("create comment as a default question when the dataset does not have questions", () => {
      const datasetInfoWithoutQuestions = {
        ...datasetInfo,
        features: {
          text_field: {
            dtype: "string",
            _type: "Value",
          },
          image_field: {
            dtype: "string",
            _type: "Image",
          },
        },
      };

      const builder = new DatasetCreationBuilder(datasetInfoWithoutQuestions);

      const datasetCreation = builder.build();

      const commentQuestion = datasetCreation.questions[0];

      expect(commentQuestion.name).toBe("comment");
      expect(commentQuestion.type.isTextType).toBeTruthy();
      expect(commentQuestion.required).toBeTruthy();
      expect(datasetCreation.questions.length).toBe(1);
    });
  });
});
