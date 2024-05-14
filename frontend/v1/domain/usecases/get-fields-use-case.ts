import { Field } from "../entities/field/Field";
import { FieldRepository } from "~/v1/infrastructure/repositories";

export class GetFieldsUseCase {
  constructor(private fieldRepository: FieldRepository) {}

  async execute(datasetId: string): Promise<Field[]> {
    const fields = await this.fieldRepository.getFields(datasetId);

    return fields.map((field) => {
      return new Field(
        field.id,
        field.name,
        field.title,
        "",
        datasetId,
        field.required,
        field.settings
      );
    });
  }
}
