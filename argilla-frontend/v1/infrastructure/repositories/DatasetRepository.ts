import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import {
  BackendDatasetFeedbackTaskResponse,
  BackendProgress,
  BackendUpdateDataset,
} from "../types/dataset";
import { largeCache, revalidateCache } from "./AxiosCache";
import { IDatasetRepository } from "@/v1/domain/services/IDatasetRepository";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";
import { Progress } from "~/v1/domain/entities/dataset/Progress";

export const DATASET_API_ERRORS = {
  ERROR_FETCHING_FEEDBACK_DATASETS: "ERROR_FETCHING_FEEDBACK_DATASETS",
  ERROR_FETCHING_WORKSPACES: "ERROR_FETCHING_WORKSPACES",
  ERROR_FETCHING_DATASET_INFO: "ERROR_FETCHING_DATASET_INFO",
  ERROR_FETCHING_WORKSPACE_INFO: "ERROR_FETCHING_WORKSPACE_INFO",
  ERROR_PATCHING_DATASET_GUIDELINES: "ERROR_PATCHING_DATASET_GUIDELINES",
  ERROR_DELETING_DATASET: "ERROR_DELETING_DATASET",
  ERROR_FETCHING_DATASET_PROGRESS: "ERROR_FETCHING_DATASET_PROGRESS",
};

export class DatasetRepository implements IDatasetRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

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
      dataset.inserted_at,
      dataset.updated_at,
      dataset.last_activity_at,
      dataset.allow_extra_metadata
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
          datasetFromBackend.inserted_at,
          datasetFromBackend.updated_at,
          datasetFromBackend.last_activity_at,
          datasetFromBackend.allow_extra_metadata
        );
      }
    );

    return [...feedbackDatasets];
  }

  async update({ id, allowExtraMetadata, guidelines }: Dataset) {
    const request: BackendUpdateDataset = {
      allow_extra_metadata: allowExtraMetadata,
      guidelines: guidelines?.trim() !== "" ? guidelines.trim() : null,
    };

    try {
      const { data } =
        await this.axios.patch<BackendDatasetFeedbackTaskResponse>(
          `/v1/datasets/${id}`,
          request
        );

      revalidateCache(`/v1/datasets/${id}`);

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

      return new Progress(
        data.total,
        data.submitted,
        data.discarded,
        data.conflicting,
        data.pending
      );
    } catch (err) {
      throw {
        response: DATASET_API_ERRORS.ERROR_DELETING_DATASET,
      };
    }
  }

  private async getDatasetById(datasetId: string) {
    try {
      const { data } = await this.axios.get(
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

  private fetchFeedbackDatasets = async (axios) => {
    try {
      const { data } = await axios.get("/v1/me/datasets");

      return data;
    } catch (err) {
      throw {
        response: DATASET_API_ERRORS.ERROR_FETCHING_FEEDBACK_DATASETS,
      };
    }
  };

  private fetchWorkspaces = async (axios) => {
    try {
      const { data } = await axios.get("v1/me/workspaces");

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
  ) => {
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
      this.fetchFeedbackDatasets(this.axios),
      this.fetchWorkspaces(this.axios),
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
