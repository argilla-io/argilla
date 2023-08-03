import { Field } from "../../entities/Field";
import { FieldRepository } from "~/v1/infrastructure/repositories";

export class UpdateFieldSettingUseCase {
  constructor(private readonly fieldRepository: FieldRepository) {}

  async execute(field: Field) {
    await this.fieldRepository.update(field);
  }
}
