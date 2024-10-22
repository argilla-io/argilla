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
  public readonly metadata: MetadataCreation[] = [];
  private readonly structures: Structure[] = [];
  private readonly splits: any[];
  public selectedSplit: any;

  constructor(public readonly name: string, datasetInfo: any) {
    this.splits = Object.entries(datasetInfo.splits).map(([name, value]) => {
      return {
        name,
        value,
      };
    });

    this.selectedSplit = this.splits[0];

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

      this.createNoMappedFields(structure);
    }

    this.setDefaultValues();
  }

  public get columns() {
    const columnNames = this.structures.map((f) => f.name);
    return ["no mapping", ...columnNames];
  }

  private setDefaultValues() {
    if (this.questions.length === 1) {
      this.questions[0].markAsRequired();
    }

    if (this.fields.length === 1) {
      this.fields[0].markAsRequired();
    }
  }

  private tryToCreateQuestion(structure: Structure) {
    if (this.isASingleLabel(structure)) {
      this.questions.push(
        new QuestionCreation(
          structure.name,
          {
            type: "label_selection",
            options: structure.options.map((o) => ({
              text: o,
              value: o,
            })),
          },
          structure.name
        )
      );

      return true;
    }

    return false;
  }

  private tryToCreateFields(structure: Structure) {
    const getFieldType = (structure: Structure) => {
      if (structure.kindObject === "Value" && structure.type === "string")
        return "text";

      if (structure.kindObject === "Image") return "image";

      if (structure.structure?.length > 0) return "chat";
    };

    const field = FieldCreation.from(
      structure.name,
      getFieldType(structure),
      structure.type
    );

    if (field) {
      this.fields.push(field);

      return true;
    }

    return false;
  }

  private tryToCreateMetadata(structure: Structure) {
    const metadata = MetadataCreation.from(structure.name, structure.type);

    if (metadata) {
      this.metadata.push(metadata);

      return true;
    }

    return false;
  }

  private createNoMappedFields(structure: Structure) {
    this.fields.push(
      FieldCreation.from(
        structure.name,
        "no mapping",
        structure.type ?? structure.kindObject
      )
    );
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
    if (type === "label_selection") {
      settings.options = [
        { text: "positive", id: "1", value: "positive" },
        { text: "negative", id: "2", value: "negative" },
        { text: "neutral", id: "3", value: "neutral" },
      ];
    }

    if (type === "multi_label_selection") {
      settings.options = [
        { text: "news", id: "1", value: "news" },
        { text: "sports", id: "2", value: "sports" },
        { text: "international", id: "3", value: "international" },
        { text: "politics", id: "4", value: "politics" },
      ];
    }

    if (type === "rating") {
      settings.options = [
        { value: 0 },
        { value: 1 },
        { value: 2 },
        { value: 3 },
        { value: 4 },
        { value: 5 },
        { value: 6 },
        { value: 7 },
        { value: 8 },
        { value: 9 },
        { value: 10 },
      ];
    }

    if (type === "ranking") {
      settings.options = [
        { text: "Option 1", value: "option1" },
        { text: "Option 2", value: "option2" },
      ];
    }

    if (type === "span") {
      settings.options = [
        { text: "organisation", id: "1", value: "organisation" },
        { text: "person", id: "2", value: "person" },
        { text: "event", id: "3", value: "event" },
      ];
      settings.allow_overlapping = true;
      settings.field = "text";
    }

    if (type === "text") {
      settings.options = [];
    }

    const currentQuestion = this.questions.find((q) => q.name === name);

    if (currentQuestion) {
      currentQuestion?.setSettings(settings);

      return;
    }

    this.questions.push(new QuestionCreation(name, settings));
  }
}
