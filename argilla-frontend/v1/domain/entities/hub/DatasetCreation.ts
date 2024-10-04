import { FieldType } from "../field/FieldType";
import { QuestionType } from "../question/QuestionType";
import { Subset } from "./Subset";

export const availableMetadataType = ["terms", "int", "float"];

export const availableFieldTypes = [
  "no mapping",
  FieldType.from("text"),
  FieldType.from("image"),
  FieldType.from("chat"),
];

export const availableQuestionTypes = [
  QuestionType.from("label_selection"),
  QuestionType.from("multi_label_selection"),
  QuestionType.from("ranking"),
  QuestionType.from("text"),
  QuestionType.from("span"),
  QuestionType.from("rating"),
];

export class DatasetCreation {
  public selectedSubset: Subset;

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

  get metadata() {
    return this.selectedSubset.metadata;
  }

  get noMapped() {
    return this.selectedSubset.noMapped;
  }
}
