import { FieldType } from "../field/FieldType";
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
  public readonly required: false;

  constructor(
    public readonly name: string,
    public title: string,
    private readonly type: string
  ) {}

  get isTextType() {
    return FieldType.from(this.type).isTextType;
  }

  get isImageType() {
    return FieldType.from(this.type).isImageType;
  }

  get isChatType() {
    return FieldType.from(this.type).isChatType;
  }

  get isCustomType() {
    return FieldType.from(this.type).isCustomType;
  }
}

class QuestionCreation {
  public readonly settings: QuestionSetting;

  constructor(
    public readonly name: string,
    public readonly required: boolean,
    settings: QuestionPrototype
  ) {
    this.settings = new QuestionSetting(settings);
  }

  get type() {
    return this.settings.type;
  }

  get options() {
    return this.settings.options;
  }
}

class Subset {
  public readonly fields: FieldCreation[] = [];
  public readonly questions: QuestionCreation[] = [];

  private readonly features: {
    name: string;
    options?: string[];
    kindObject: "Value" | "Image" | "ClassLabel";
    type: "string" | "int32" | "int64";
  }[] = [];

  constructor(public readonly name: string, datasetInfo: any) {
    for (const [name, value] of Object.entries<Feature>(datasetInfo.features)) {
      this.features.push({
        name,
        options: value.names,
        kindObject: value._type,
        type: value.dtype,
      });
    }

    this.createFields();
    this.createQuestions();
  }

  private createQuestions() {
    for (const feat of this.features) {
      if (feat.kindObject === "ClassLabel") {
        this.questions.push(
          new QuestionCreation(feat.name, false, {
            type: "label_selection",
            options: feat.options,
          })
        );
      }
    }

    if (this.questions.length === 0) {
      this.questions.push(
        new QuestionCreation("comment", true, { type: "text" })
      );
    }
  }

  private createFields() {
    for (const feat of this.features) {
      if (feat.kindObject === "Value") {
        this.fields.push(new FieldCreation(feat.name, feat.name, "text"));
      }

      if (feat.kindObject === "Image") {
        this.fields.push(new FieldCreation(feat.name, feat.name, "image"));
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
