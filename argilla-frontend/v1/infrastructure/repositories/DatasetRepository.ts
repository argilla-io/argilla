import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import {
  BackendDataset,
  BackendDatasetFeedbackTaskResponse,
  BackendDatasetWithWorkspace,
  BackendProgress,
  BackendUpdateDataset,
} from "../types/dataset";
import { Response } from "../types";
import { largeCache, revalidateCache } from "./AxiosCache";
import {
  DatasetId,
  IDatasetRepository,
} from "@/v1/domain/services/IDatasetRepository";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";
import { Progress } from "~/v1/domain/entities/dataset/Progress";

export const DATASET_API_ERRORS = {
  ERROR_FETCHING_FEEDBACK_DATASETS: "ERROR_FETCHING_FEEDBACK_DATASETS",
  ERROR_FETCHING_WORKSPACES: "ERROR_FETCHING_WORKSPACES",
  ERROR_FETCHING_DATASET_INFO: "ERROR_FETCHING_DATASET_INFO",
  ERROR_CREATING_DATASET: "ERROR_CREATING_DATASET",
  ERROR_FETCHING_WORKSPACE_INFO: "ERROR_FETCHING_WORKSPACE_INFO",
  ERROR_PATCHING_DATASET_GUIDELINES: "ERROR_PATCHING_DATASET_GUIDELINES",
  ERROR_DELETING_DATASET: "ERROR_DELETING_DATASET",
  ERROR_FETCHING_DATASET_PROGRESS: "ERROR_FETCHING_DATASET_PROGRESS",
};

export class DatasetRepository implements IDatasetRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async create({ name, workspaceId }): Promise<DatasetId> {
    try {
      const { data } = await this.axios.post<BackendDataset>("/v1/datasets", {
        name,
        workspace_id: workspaceId,
      });

      return data.id;
    } catch (err) {
      throw {
        response: DATASET_API_ERRORS.ERROR_CREATING_DATASET,
      };
    }
  }

  async publish(datasetId: string): Promise<boolean> {
    try {
      const { data } = await this.axios.put(
        `/v1/datasets/${datasetId}/publish`
      );

      revalidateCache(`/v1/datasets/${datasetId}`);

      return data.id === datasetId;
    } catch (err) {
      throw {
        response: DATASET_API_ERRORS.ERROR_FETCHING_DATASET_INFO,
      };
    }
  }

  async import({ name, datasetId, subset, split }): Promise<void> {
    try {
      await this.axios.post<BackendDataset>(
        `/v1/datasets/${datasetId}/import`,
        {
          name,
          subset,
          split,
        }
      );
    } catch (err) {
      throw {
        response: DATASET_API_ERRORS.ERROR_FETCHING_DATASET_INFO,
      };
    }
  }

  async getById(id: string): Promise<Dataset> {
    const dataset = await this.getDatasetById(id);
    const workspace = await this.getWorkspaceById(dataset.workspace_id);

    return new Dataset(
      dataset.id,
      dataset.name,
      dataset.guidelines,
      dataset.status,
      dataset.workspace_id,
      workspace,
      dataset.allow_extra_metadata,
      {
        strategy: dataset.distribution.strategy,
        minSubmitted: dataset.distribution.min_submitted,
      },
      dataset.inserted_at,
      dataset.updated_at,
      dataset.last_activity_at
    );
  }

  async getAll(): Promise<Dataset[]> {
    const response = await this.getDatasets();

    const feedbackDatasets = response.feedbackDatasetsWithWorkspaces.map(
      (datasetFromBackend) => {
        return new Dataset(
          datasetFromBackend.id,
          datasetFromBackend.name,
          datasetFromBackend.guidelines,
          datasetFromBackend.status,
          datasetFromBackend.workspace_id,
          datasetFromBackend.workspace_name,
          datasetFromBackend.allow_extra_metadata,
          {
            strategy: datasetFromBackend.distribution.strategy,
            minSubmitted: datasetFromBackend.distribution.min_submitted,
          },
          datasetFromBackend.inserted_at,
          datasetFromBackend.updated_at,
          datasetFromBackend.last_activity_at
        );
      }
    );

    return [...feedbackDatasets];
  }

  async update({ id, ...dataset }: Partial<Dataset>) {
    const request: Partial<BackendUpdateDataset> = {};

    if ("allowExtraMetadata" in dataset) {
      request.allow_extra_metadata = dataset.allowExtraMetadata;
    }

    if ("guidelines" in dataset) {
      request.guidelines = dataset.guidelines?.trim() ?? null;
    }

    if ("distribution" in dataset) {
      request.distribution = {
        strategy: dataset.distribution.strategy,
        min_submitted: dataset.distribution.minSubmitted,
      };
    }

    try {
      const { data } =
        await this.axios.patch<BackendDatasetFeedbackTaskResponse>(
          `/v1/datasets/${id}`,
          request
        );

      revalidateCache(`/v1/datasets/${id}`);
      revalidateCache(`/v1/datasets/${id}/progress`);

      return {
        when: data.updated_at,
      };
    } catch (err) {
      throw {
        response: DATASET_API_ERRORS.ERROR_PATCHING_DATASET_GUIDELINES,
      };
    }
  }

  async delete(datasetId: string) {
    try {
      await this.axios.delete(`/v1/datasets/${datasetId}`, {
        validateStatus: (status) => status === 200,
      });
    } catch (err) {
      throw {
        response: DATASET_API_ERRORS.ERROR_DELETING_DATASET,
      };
    }
  }

  async getProgress(datasetId: string): Promise<Progress> {
    try {
      const { data } = await this.axios.get<BackendProgress>(
        `/v1/datasets/${datasetId}/progress`,
        largeCache()
      );

      return new Progress(data.total, data.completed, data.pending);
    } catch (err) {
      throw {
        response: DATASET_API_ERRORS.ERROR_DELETING_DATASET,
      };
    }
  }

  private async getDatasetById(datasetId: string) {
    try {
      const { data } = await this.axios.get<BackendDataset>(
        `/v1/datasets/${datasetId}`,
        largeCache()
      );

      return data;
    } catch (err) {
      throw {
        response: DATASET_API_ERRORS.ERROR_FETCHING_DATASET_INFO,
      };
    }
  }

  private async getWorkspaceById(workspaceId: string) {
    try {
      const { data: responseWorkspace } = await this.axios.get(
        `/v1/workspaces/${workspaceId}`,
        largeCache()
      );

      const { name } = responseWorkspace || { name: null };

      return name;
    } catch (err) {
      throw {
        response: DATASET_API_ERRORS.ERROR_FETCHING_WORKSPACE_INFO,
      };
    }
  }

  private fetchFeedbackDatasets = async () => {
    try {
      const { data } = await this.axios.get<Response<BackendDataset[]>>(
        "/v1/me/datasets"
      );

      return data;
    } catch (err) {
      throw {
        response: DATASET_API_ERRORS.ERROR_FETCHING_FEEDBACK_DATASETS,
      };
    }
  };

  private fetchWorkspaces = async () => {
    try {
      const { data } = await this.axios.get("v1/me/workspaces");

      return data.items;
    } catch (err) {
      throw {
        response: DATASET_API_ERRORS.ERROR_FETCHING_WORKSPACES,
      };
    }
  };

  private factoryFeedbackDatasetsWithCorrespondingWorkspaceName = (
    feedbackDatasets,
    workspaces
  ): BackendDatasetWithWorkspace[] => {
    const newFeedbackDatasets = feedbackDatasets.map((feedbackDataset) => {
      return {
        ...feedbackDataset,
        workspace_name:
          workspaces.find(
            (workspace) => workspace.id === feedbackDataset.workspace_id
          )?.name || "",
      };
    });
    return newFeedbackDatasets;
  };

  private getDatasets = async () => {
    const [newDatasets, workspaces] = await Promise.all([
      this.fetchFeedbackDatasets(),
      this.fetchWorkspaces(),
    ]);

    const { items: feedbackTaskDatasets } = newDatasets;

    const feedbackDatasetsWithWorkspaces =
      this.factoryFeedbackDatasetsWithCorrespondingWorkspaceName(
        feedbackTaskDatasets,
        workspaces
      );

    return { feedbackDatasetsWithWorkspaces };
  };
}
