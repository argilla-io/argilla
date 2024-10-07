import { FieldType } from "../field/FieldType";
import { MetadataType } from "../metadata/MetadataType";
import { QuestionType } from "../question/QuestionType";
import { Subset } from "./Subset";

export const availableMetadataTypes = [
  MetadataType.from("int32"),
  MetadataType.from("int64"),
  MetadataType.from("float32"),
  MetadataType.from("float64"),
  MetadataType.from("terms"),
];

export const availableFieldTypes = [
  FieldType.from("no mapping"),
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
}
