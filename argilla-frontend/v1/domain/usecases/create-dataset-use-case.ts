import { DatasetCreation } from "../entities/hub/DatasetCreation";
import { IDatasetRepository } from "../services/IDatasetRepository";
import {
  FieldRepository,
  QuestionRepository,
} from "~/v1/infrastructure/repositories";

export class CreateDatasetUseCase {
  constructor(
    private readonly datasetRepository: IDatasetRepository,
    private readonly questionRepository: QuestionRepository,
    private readonly fieldRepository: FieldRepository
  ) {}

  async execute(dataset: DatasetCreation) {
    // TODO: Crear workspace if not exists

    const datasetCreated = await this.datasetRepository.create({
      name: dataset.name,
      workspaceId: "108b045c-a82e-4c75-a61b-0cddfb22c4c8",
    });

    for (const field of dataset.fields) {
      await this.fieldRepository.create(datasetCreated, field);
    }

    for (const question of dataset.questions) {
      await this.questionRepository.create(datasetCreated, question);
    }

    await this.datasetRepository.publish(datasetCreated);

    await this.datasetRepository.import({
      datasetId: datasetCreated,
      name: dataset.name,
      subset: dataset.selectedSubset.name,
      split: dataset.selectedSubset.selectedSplit.name,
    });

    return datasetCreated;
  }
}
