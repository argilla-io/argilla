import { Field } from "../field/Field";
import { Workspace } from "../workspace/Workspace";
import { Subset } from "./Subset";

export class DatasetCreation {
  public selectedSubset: Subset;

  public readonly firstRecord: {};
  public workspace: Workspace;

  constructor(
    public readonly repoId: string,
    public name: string,
    private readonly subset: Subset[]
  ) {
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

  get textTypeFields() {
    return this.selectedSubset.fields.filter((f) => f.settings.type.isTextType);
  }

  get mappedFields() {
    return this.fields.filter(
      (f) => f.type.value !== "no mapping" && f.name !== "id"
    );
  }

  get questions() {
    return this.selectedSubset.questions;
  }

  get mappedQuestions() {
    return this.questions.filter((q) => q.column !== "no mapping");
  }

  get metadata() {
    return this.selectedSubset.metadata;
  }

  get columns() {
    return this.selectedSubset.columns;
  }

  get mappings() {
    const mappings: {
      fields: { source: string; target: string }[];
      metadata: { source: string; target: string }[];
      suggestions: { source: string; target: string }[];
      external_id?: string;
    } = {
      fields: this.mappedFields.map((field) => ({
        source: field.name,
        target: field.name,
      })),
      metadata: this.metadata.map((metadata) => ({
        source: metadata.name,
        target: metadata.name,
      })),
      suggestions: this.mappedQuestions.map((question) => ({
        source: question.column,
        target: question.name,
      })),
    };

    if (this.fields.some((f) => f.name === "id")) {
      mappings.external_id = "id";
    }

    return mappings;
  }

  createFields(firstRawRecord: unknown): Field[] {
    return this.mappedFields.map((field) => {
      return new Field(
        field.name,
        field.name,
        field.title,
        this.name,
        field.required,
        field.settings,
        {
          fields: firstRawRecord,
        }
      );
    });
  }

  get isValid(): boolean {
    return this.validate().question.length === 0;
  }

  validate(): Record<"question", string[]> {
    const validations: Record<"question", string[]> = {
      question: [],
    };

    if (this.questions.length === 0) {
      validations.question.push("datasetCreation.atLeastOneQuestion");
    }

    if (!this.questions.some((q) => q.required)) {
      validations.question.push("datasetCreation.atLeastOneRequired");
    }

    if (this.questions.some((q) => !q.isValid)) {
      validations.question.push("datasetCreation.hasInvalidQuestions");
    }

    return validations;
  }
}
