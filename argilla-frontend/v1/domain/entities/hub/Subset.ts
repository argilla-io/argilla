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
  public readonly noMapped: Structure[] = [];
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

    for (const structure of this.structures) {
      if (this.tryToCreateFields(structure)) continue;

      if (this.tryToCreateQuestion(structure)) continue;

      if (this.tryToCreateMetadata(structure)) continue;

      this.noMapped.push(structure);
    }

    this.setDefaultValues();
  }

  private setDefaultValues() {
    if (this.questions.length === 0) {
      this.questions.push(
        new QuestionCreation("comment", true, {
          type: "text",
        })
      );
    }

    if (this.questions.length === 1) {
      this.questions[0].markAsRequired();
    }

    if (this.fields.length === 0) {
      this.fields.push(new FieldCreation("prompt", "text"));
    }

    if (this.fields.length === 1) {
      this.fields[0].markAsRequired();
    }
  }

  private tryToCreateQuestion(structure: Structure) {
    if (this.isASingleLabel(structure)) {
      this.questions.push(
        new QuestionCreation(structure.name, false, {
          type: "label_selection",
          options: structure.options,
        })
      );

      return true;
    }

    return false;
  }

  private tryToCreateFields(structure: Structure) {
    if (this.isTextField(structure)) {
      this.fields.push(new FieldCreation(structure.name, "text"));
    } else if (this.isImageField(structure)) {
      this.fields.push(new FieldCreation(structure.name, "image"));
    } else if (this.isChatField(structure)) {
      this.fields.push(new FieldCreation(structure.name, "chat"));
    } else {
      return false;
    }

    return true;
  }

  private tryToCreateMetadata(structure: Structure) {
    const metadataTypes = ["int32", "int64", "float32", "float64"];

    if (metadataTypes.includes(structure.type)) {
      this.metadata.push(
        new MetadataCreation(structure.name, structure.type as MetadataTypes)
      );

      return true;
    }

    return false;
  }

  private isASingleLabel(structure: Structure) {
    return structure.kindObject === "ClassLabel";
  }

  public removeQuestion(name: string) {
    const index = this.questions.findIndex((q) => q.name === name);
    if (index !== -1) {
      this.questions.splice(index, 1);
    }
  }

  public addQuestion(name: string, settings: QuestionPrototype) {
    const { type } = settings;

    if (type === "label_selection" || type === "multi_label_selection") {
      settings.options = [
        { name: "positive" },
        { name: "negative" },
        { name: "neutral" },
      ];
    }

    if (type === "rating") {
      settings.options = [
        { value: 1 },
        { value: 2 },
        { value: 3 },
        { value: 4 },
        { value: 5 },
      ];
    }

    if (type === "ranking") {
      settings.options = [
        { text: "Option 1", value: "option1" },
        { text: "Option 2", value: "option2" },
      ];
    }

    this.questions.push(new QuestionCreation(name, false, settings));
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
}
