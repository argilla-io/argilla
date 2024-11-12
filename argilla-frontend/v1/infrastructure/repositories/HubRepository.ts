import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { PublicNuxtAxiosInstance } from "../services";
import { DatasetCreation } from "~/v1/domain/entities/hub/DatasetCreation";

export const enum HUB_REPOSITORY_ERRORS {
  NOT_EXIST = "ERROR_FETCHING_DATASET",
}

export class HubRepository {
  private axios: NuxtAxiosInstance;
  constructor(axios: PublicNuxtAxiosInstance) {
    this.axios = axios.makePublic({
      enableErrors: false,
    });
  }

  async getDatasetCreation(repoId: string): Promise<any> {
    try {
      const { data } = await this.axios.get(
        `https://datasets-server.huggingface.co/info?dataset=${encodeURIComponent(
          repoId
        )}`
      );

      return data.dataset_info;
    } catch (e) {
      throw {
        response: HUB_REPOSITORY_ERRORS.NOT_EXIST,
      };
    }
  }

  async getColumnsDistributions(
    repoId: string,
    subset: string,
    split: string
  ): Promise<any> {
    // Example call https://datasets-server.huggingface.co/statistics?dataset=derek-thomas/ScienceQA&config=default&split=train
    const { data } = await this.axios.get(
      "https://datasets-server.huggingface.co/statistics",
      {
        params: {
          dataset: encodeURIComponent(repoId),
          config: subset,
          split,
        },
      }
    );

    const distributions = [];
    for (const columnStats of data.statistics) {
      const columnDistribution = {
        name: columnStats.column_name,
        type: columnStats.column_type,
        values: null,
      };

      const stats = columnStats.column_statistics;

      switch (columnDistribution.type) {
        // Helpful for ratings
        case "int":
          columnDistribution.values = { min: stats.min, max: stats.max };
          break;
        // Helpful for label questions or terms metadata
        case "string_label":
          columnDistribution.values = [];
          for (const key of stats.frequencies) {
            columnDistribution.values.push(key);
          }
          break;
        default:
          // For other cases, the values will be null
          break;
      }
      distributions.push(columnDistribution);
    }

    return distributions;
  }

  async getFirstRecord(dataset: DatasetCreation): Promise<any> {
    try {
      const { repoId, selectedSubset } = dataset;
      const { data } = await this.axios.get(
        `https://datasets-server.huggingface.co/first-rows?dataset=${encodeURIComponent(
          repoId
        )}&split=${selectedSubset.selectedSplit.name}&config=${
          selectedSubset.name
        }`
      );

      return data.rows[0].row;
    } catch {
      return {};
    }
  }
}
