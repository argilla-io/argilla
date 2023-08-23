import { Field } from "../../entities/field/Field";
import { FieldRepository } from "~/v1/infrastructure/repositories";

export class UpdateFieldSettingUseCase {
  constructor(private readonly fieldRepository: FieldRepository) {}

  async execute(field: Field) {
    if (!field.isFieldValid) {
      throw new Error("Field is not valid for update");
    }

    const { title, settings } = await this.fieldRepository.update(field);

    field.update(title, settings);
  }
}
