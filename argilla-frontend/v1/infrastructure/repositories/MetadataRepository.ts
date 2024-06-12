import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { BackendMetadata, Response } from "../types";
import { MetadataMetricsRepository } from "./MetadataMetricsRepository";
import { mediumCache, revalidateCache } from "./AxiosCache";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";

const METADATA_API_ERRORS = {
  ERROR_FETCHING_METADATA: "ERROR_FETCHING_METADATA",
  ERROR_UPDATING_METADATA: "ERROR_UPDATING_METADATA",
};

export class MetadataRepository {
  private readonly metadataMetricsRepository: MetadataMetricsRepository;
  constructor(private readonly axios: NuxtAxiosInstance) {
    this.metadataMetricsRepository = new MetadataMetricsRepository(axios);
  }

  async getMetadataFilters(datasetId: string) {
    try {
      const items = await this.getMetadataProperties(datasetId);

      return this.completeEmptyMetadataFilters(items);
    } catch (err) {
      throw {
        response: METADATA_API_ERRORS.ERROR_FETCHING_METADATA,
      };
    }
  }

  async getMetadataProperties(datasetId: string) {
    try {
      // TODO: Review this endpoint, for admin should be /v1/datasets/${datasetId}/metadata-properties without ME.
      const { data } = await this.axios.get<Response<BackendMetadata[]>>(
        `/v1/me/datasets/${datasetId}/metadata-properties`,
        mediumCache()
      );

      return data.items;
    } catch (err) {
      throw {
        response: METADATA_API_ERRORS.ERROR_FETCHING_METADATA,
      };
    }
  }

  async update(metadata: Metadata): Promise<BackendMetadata> {
    try {
      const { data } = await this.axios.patch<BackendMetadata>(
        `/v1/metadata-properties/${metadata.id}`,
        this.createRequest(metadata)
      );

      revalidateCache(`/v1/datasets/${metadata.datasetId}/metadata-properties`);

      return data;
    } catch (err) {
      throw {
        response: METADATA_API_ERRORS.ERROR_UPDATING_METADATA,
      };
    }
  }

  private createRequest({
    title,
    visibleForAnnotators,
  }: Metadata): Partial<BackendMetadata> {
    return {
      title,
      visible_for_annotators: visibleForAnnotators,
    };
  }

  private async completeEmptyMetadataFilters(
    metadataFilters?: BackendMetadata[]
  ): Promise<BackendMetadata[]> {
    if (!metadataFilters) return [];

    const metadataWithNoValues = metadataFilters.filter((m) => {
      if (m.settings.type === "terms") {
        return !m.settings.values;
      }

      return m.settings.max === null && m.settings.min === null;
    });

    const metrics = await Promise.allSettled(
      metadataWithNoValues.map((m) =>
        this.metadataMetricsRepository.getMetric(m.id)
      )
    );

    metrics.forEach((response) => {
      if (response.status === "rejected") return;
      const metric = response.value;

      const metadata = metadataFilters.find((m) => m.id === metric.id);

      if (metadata.settings.type === "terms") {
        metadata.settings.values = metric.values.map((item) => item.term);
      } else {
        metadata.settings.max = metric.max!;
        metadata.settings.min = metric.min!;
      }
    });

    return metadataFilters;
  }
}
