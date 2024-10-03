import { FieldType } from "../field/FieldType";
import { QuestionPrototype } from "../question/QuestionSetting";
import { Feature } from "./DatasetCreationBuilder";
import { FieldCreation } from "./FieldCreation";
import { MetadataTypes, MetadataCreation } from "./MetadataCreation";
import { QuestionCreation } from "./QuestionCreation";

type Structure = {
  name: string;
  options?: string[];
  structure?: Structure[];
  kindObject?: "Value" | "Image" | "ClassLabel";
  type?: "string" | MetadataTypes;
};

export class Subset {
  public readonly fields: FieldCreation[] = [];
  public readonly questions: QuestionCreation[] = [];
  public readonly metadata: any[] = [];
  private readonly structures: Structure[] = [];

  constructor(public readonly name: string, datasetInfo: any) {
    for (const [name, value] of Object.entries<Feature>(datasetInfo.features)) {
      if (Array.isArray(value)) {
        this.structures.push({
          name,
          structure: value.map((v) => {
            const [key, value] = Object.entries<any>(v)[0];

            return {
              name: key,
              kindObject: value._type,
              type: value.dtype,
            };
          }),
        });
      } else {
        this.structures.push({
          name,
          options: value.names,
          kindObject: value._type,
          type: value.dtype,
        });
      }
    }

    this.createFields();
    this.createQuestions();
    this.createMetadata();
  }

  private createQuestions() {
    for (const structure of this.structures) {
      if (structure.kindObject === "ClassLabel") {
        this.questions.push(
          new QuestionCreation(structure.name, false, {
            type: "label_selection",
            options: structure.options,
          })
        );
      }
    }

    if (this.questions.length === 0) {
      this.questions.push(
        new QuestionCreation("comment", false, {
          type: "text",
        })
      );
    }

    if (this.questions.length === 1) {
      this.questions[0].markAsRequired();
    }
  }

  public removeQuestion(name: string) {
    const index = this.questions.findIndex((q) => q.name === name);
    if (index !== -1) {
      this.questions.splice(index, 1);
    }
  }

  public addQuestion(name: string, settings: QuestionPrototype) {
    const { type } = settings;

    if (type === "label_selection") {
      settings.options = [
        { name: "positive" },
        { name: "negative" },
        { name: "neutral" },
      ];
    }

    if (type === "ranking") {
      settings.options = [
        { text: "Option 1", value: "option1" },
        { text: "Option 2", value: "option2" },
        { text: "Option 3", value: "option3" },
      ];
    }

    this.questions.push(new QuestionCreation(name, false, settings));
  }

  private createFields() {
    for (const structure of this.structures) {
      if (this.isTextField(structure)) {
        this.fields.push(
          new FieldCreation(structure.name, FieldType.from("text"))
        );
      } else if (this.isImageField(structure)) {
        this.fields.push(
          new FieldCreation(structure.name, FieldType.from("image"))
        );
      } else if (this.isChatField(structure)) {
        this.fields.push(
          new FieldCreation(structure.name, FieldType.from("chat"))
        );
      }
    }

    if (this.fields.length === 0) {
      this.fields.push(new FieldCreation("prompt", FieldType.from("text")));
    }

    if (this.fields.length === 1) {
      this.fields[0].markAsRequired();
    }
  }

  private isTextField(structure: Structure) {
    return structure.kindObject === "Value" && structure.type === "string";
  }

  private isImageField(structure: Structure) {
    return structure.kindObject === "Image";
  }

  private isChatField(structure: Structure) {
    return structure.structure?.length > 0;
  }

  private createMetadata() {
    const metadataTypes = ["int32", "int64", "float32", "float64"];
    for (const structure of this.structures) {
      if (metadataTypes.includes(structure.type)) {
        this.metadata.push(
          new MetadataCreation(structure.name, structure.type as MetadataTypes)
        );
      }
    }
  }
}
