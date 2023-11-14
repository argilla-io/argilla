import { Vector } from "../../entities/vector/Vector";
import { VectorRepository } from "~/v1/infrastructure/repositories";

export class UpdateVectorSettingUseCase {
  constructor(private readonly vectorRepository: VectorRepository) {}

  async execute(vector: Vector) {
    if (!vector.isValid) {
      throw new Error("Vector is not valid for update");
    }

    const { title } = await this.vectorRepository.update(vector);

    vector.update(title);
  }
}
