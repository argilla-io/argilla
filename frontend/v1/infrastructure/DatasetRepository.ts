import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Store } from "vuex";
import { Dataset } from "../domain/entities/Dataset";
import { IDatasetRepository } from "../domain/services/IDatasetRepository";
import {
  URL_GET_V1_DATASETS,
  URL_GET_WORKSPACES,
} from "~/utils/url.properties";

export const TYPE_OF_FEEDBACK = {
  ERROR_FETCHING_FEEDBACK_DATASETS: "ERROR_FETCHING_FEEDBACK_DATASETS",
  ERROR_FETCHING_WORKSPACES: "ERROR_FETCHING_WORKSPACES",
  ERROR_FETCHING_DATASET_INFO: "ERROR_FETCHING_DATASET_INFO",
  ERROR_FETCHING_WORKSPACE_INFO: "ERROR_FETCHING_WORKSPACE_INFO",
};

export class DatasetRepository implements IDatasetRepository {
  constructor(
    private readonly axios: NuxtAxiosInstance,
    private readonly store: Store<unknown>
  ) {}

  async getById(id: string): Promise<Dataset> {
    const dataset = await this.getDatasetById(id);
    const workspace = await this.getWorkspaceById(dataset.workspace_id);

    return new Dataset(
      dataset.id,
      dataset.name,
      "FeedbackTask",
      dataset.guidelines,
      dataset.status,
      dataset.workspace_id,
      workspace,
      {},
      dataset.inserted_at,
      dataset.updated_at
    );
  }

  async getAll(): Promise<Dataset[]> {
    const response = await this.getDatasets();

    const otherDatasets = response.oldDatasets.map((dataset) => {
      return new Dataset(
        dataset.id,
        dataset.name,
        dataset.task,
        "",
        "",
        "",
        dataset.workspace,
        dataset.tags,
        dataset.created_at,
        dataset.last_updated
      );
    });

    const feedbackDatasets = response.feedbackDatasetsWithWorkspaces.map(
      (datasetFromBackend) => {
        return new Dataset(
          datasetFromBackend.id,
          datasetFromBackend.name,
          "FeedbackTask",
          datasetFromBackend.guidelines,
          datasetFromBackend.status,
          datasetFromBackend.workspace_id,
          datasetFromBackend.workspace_name,
          {},
          datasetFromBackend.inserted_at,
          datasetFromBackend.updated_at
        );
      }
    );

    return [...otherDatasets, ...feedbackDatasets];
  }

  private async getDatasetById(datasetId: string) {
    try {
      const { data } = await this.axios.get(`/v1/datasets/${datasetId}`);

      return data;
    } catch (err) {
      throw {
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_DATASET_INFO,
      };
    }
  }

  private async getWorkspaceById(workspaceId: string) {
    try {
      const { data: responseWorkspace } = await this.axios.get(
        `/v1/workspaces/${workspaceId}`
      );

      const { name } = responseWorkspace || { name: null };

      return name;
    } catch (err) {
      throw {
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_WORKSPACE_INFO,
      };
    }
  }

  private fetchFeedbackDatasets = async (axios) => {
    const url = URL_GET_V1_DATASETS;
    try {
      const { data } = await axios.get(url);

      return data;
    } catch (err) {
      throw {
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_FEEDBACK_DATASETS,
      };
    }
  };

  private fetchWorkspaces = async (axios) => {
    const url = URL_GET_WORKSPACES;
    try {
      const { data } = await axios.get(url);

      return data;
    } catch (err) {
      throw {
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_WORKSPACES,
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
    const [oldDatasets, newDatasets, workspaces] = await Promise.all([
      this.store.dispatch("entities/datasets/fetchAll"),
      this.fetchFeedbackDatasets(this.axios),
      this.fetchWorkspaces(this.axios),
    ]);

    const { items: feedbackTaskDatasets } = newDatasets;

    const feedbackDatasetsWithWorkspaces =
      this.factoryFeedbackDatasetsWithCorrespondingWorkspaceName(
        feedbackTaskDatasets,
        workspaces
      );

    return { oldDatasets, feedbackDatasetsWithWorkspaces };
  };
}
