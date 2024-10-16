import { DatasetCreation } from "../entities/hub/DatasetCreation";
import { Workspace } from "../entities/workspace/Workspace";
import { DatasetId, IDatasetRepository } from "../services/IDatasetRepository";
import { JobRepository } from "~/v1/infrastructure/repositories/JobRepository";
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
    private readonly metadataRepository: MetadataRepository,
    private readonly jobRepository: JobRepository
  ) {}

  async execute(dataset: DatasetCreation): Promise<DatasetId | null> {
    if (!dataset.workspace) {
      const workspace = await this.workspaceRepository.create(
        dataset.workspace.name
      );

      dataset.workspace = new Workspace(workspace.id, workspace.name);
    }

    const datasetCreated = await this.datasetRepository.create(dataset);

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

      const jobId = await this.datasetRepository.import(
        datasetCreated,
        dataset
      );

      while (true) {
        // TODO: what happen if the status is queued more than X seconds????
        const status = await this.jobRepository.getJobStatus(jobId);

        if (status.isFailed) break;

        if (status.isQueued) continue;

        if (status.isStarted) {
          revalidateCache(`/v1/datasets/${datasetCreated}/progress`);
          const progress = await this.datasetRepository.getProgress(
            datasetCreated
          );

          if (progress.hasAtLeastTenRecord) {
            break;
          }
        }
      }

      return datasetCreated;
    } catch {
      this.datasetRepository.delete(datasetCreated);

      return null;
    }
  }
}
