import { DatasetCreation } from "../entities/hub/DatasetCreation";
import { Workspace } from "../entities/workspace/Workspace";
import { DatasetId, IDatasetRepository } from "../services/IDatasetRepository";
import { Debounce } from "~/v1/infrastructure/services";
import {
  FieldRepository,
  MetadataRepository,
  QuestionRepository,
  revalidateCache,
  WorkspaceRepository,
} from "~/v1/infrastructure/repositories";

export class CreateDatasetUseCase {
  constructor(
    private readonly datasetRepository: IDatasetRepository,
    private readonly workspaceRepository: WorkspaceRepository,
    private readonly questionRepository: QuestionRepository,
    private readonly fieldRepository: FieldRepository,
    private readonly metadataRepository: MetadataRepository
  ) {}

  async execute(dataset: DatasetCreation): Promise<DatasetId | null> {
    if (!dataset.workspace.id) {
      const workspace = await this.workspaceRepository.create(
        dataset.workspace.name
      );

      dataset.workspace = new Workspace(workspace.id, workspace.name);
    }

    const datasetCreated = await this.datasetRepository.create(dataset);

    if (!datasetCreated) return null;

    try {
      for (const field of dataset.mappedFields) {
        await this.fieldRepository.create(datasetCreated, field);
      }

      for (const question of dataset.questions) {
        await this.questionRepository.create(datasetCreated, question);
      }

      for (const metadata of dataset.metadata) {
        await this.metadataRepository.create(datasetCreated, metadata);
      }

      await this.datasetRepository.publish(datasetCreated);

      await this.datasetRepository.import(datasetCreated, dataset);

      let retries = 0;
      const debounce = Debounce.from(3000);

      while (retries < 10) {
        revalidateCache(`/v1/datasets/${datasetCreated}/progress`);

        const progress = await this.datasetRepository.getProgress(
          datasetCreated
        );

        if (progress.hasAtLeastTenRecord) {
          break;
        }

        await debounce.wait();
        retries++;
      }

      return datasetCreated;
    } catch {
      this.datasetRepository.delete(datasetCreated);

      return null;
    }
  }
}
