import { any } from "@codescouts/test/jest";
import { info } from "sass";
import { FieldType } from "../field/FieldType";
import { QuestionType } from "../question/QuestionType";
import {
  QuestionSetting,
  QuestionPrototype,
} from "../question/QuestionSetting";

interface Feature {
  dtype: "string" | "int32" | "int64";
  _type: "Value" | "Image" | "ClassLabel";
  names?: string[];
}

class FieldCreation {
  public required = false;
  public readonly type: FieldType;
  constructor(public readonly name: string, type: string) {
    this.type = FieldType.from(type);
  }

  get title() {
    return this.name;
  }

  markAsRequired() {
    this.required = true;
  }
}

class QuestionCreation {
  public readonly settings: QuestionSetting;

  constructor(
    public readonly name: string,
    public required: boolean,
    settings: QuestionPrototype
  ) {
    this.settings = new QuestionSetting(settings);
  }

  get title() {
    return this.name;
  }

  get type() {
    return this.settings.type;
  }

  set type(value: QuestionType) {
    this.settings.type = value;
  }

  get options() {
    return this.settings.options;
  }

  markAsRequired() {
    this.required = true;
  }
}
type MetadataTypes = "int32" | "int64" | "float32" | "float64";

class MetadataCreation {
  public constructor(
    public readonly name: string,
    public readonly type: MetadataTypes
  ) {}
}

type Structure = {
  name: string;
  options?: string[];
  structure?: Structure[];
  kindObject?: "Value" | "Image" | "ClassLabel";
  type?: "string" | MetadataTypes;
};

class Subset {
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
        new QuestionCreation("comment", true, { type: "text" })
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

  public addQuestion(name: string, type: string) {
    this.questions.push(new QuestionCreation(name, true, { type }));
  }

  private createFields() {
    for (const structure of this.structures) {
      if (this.isTextField(structure)) {
        this.fields.push(new FieldCreation(structure.name, "text"));
      } else if (this.isImageField(structure)) {
        this.fields.push(new FieldCreation(structure.name, "image"));
      } else if (this.isChatField(structure)) {
        this.fields.push(new FieldCreation(structure.name, "chat"));
      }
    }

    if (this.fields.length === 0) {
      this.fields.push(new FieldCreation("prompt", "text"));
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

class DatasetCreation {
  private selectedSubset: Subset;

  constructor(private readonly subset: Subset[]) {
    this.selectedSubset = subset[0];
  }

  changeSubset(name: string) {
    this.selectedSubset = this.subset.find((s) => s.name === name);
  }

  get hasMoreThanOneSubset() {
    return this.subset.length > 1;
  }

  get subsets() {
    return this.subset.map((s) => s.name);
  }

  get fields() {
    return this.selectedSubset.fields;
  }

  get questions() {
    return this.selectedSubset.questions;
  }
}

export class DatasetCreationBuilder {
  private readonly subsets: Subset[] = [];
  constructor(datasetInfo: any) {
    if (datasetInfo.default) {
      for (const [name, value] of Object.entries<Feature>(datasetInfo)) {
        this.subsets.push(new Subset(name, value));
      }
    } else {
      this.subsets.push(new Subset("default", datasetInfo));
    }
  }

  build(): DatasetCreation {
    return new DatasetCreation(this.subsets);
  }
}
