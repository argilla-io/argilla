import { Field } from "../entities/field/Field";
import { IFieldRepository } from "../services/IFieldRepository";

export class GetDatasetFieldsGroupedUseCase {
  constructor(private readonly fieldRepository: IFieldRepository) {}

  async execute(datasetId: string): Promise<Field[]> {
    const backendFields = await this.fieldRepository.getFields(datasetId);

    const fields = backendFields.map((field) => {
      return new Field(
        field.id,
        field.name,
        field.title,
        datasetId,
        field.required,
        field.settings
      );
    });

    return this.groupFieldsByType(fields);
  }

  private groupFieldsByType(fields: Field[]): Field[] {
    const groupedFields: Field[] = [];
    for (const field of fields) {
      if (groupedFields.some((f) => f.settings.type === field.settings.type))
        continue;

      groupedFields.push(field);
    }

    return groupedFields;
  }
}
