import { Context } from "@nuxt/types";
import Container, { register } from "ts-injecty";
import { Registration } from "ts-injecty/types";
import { DatasetRepository } from "@/v1/infrastructure/DatasetRepository";
import { GetDatasetsUseCase } from "@/v1/domain/usecases/get-datasets-use-case";
import { useDatasets } from "@/v1/infrastructure/DatasetsStorage";
import { useDataset } from "@/v1/infrastructure/DatasetStorage";
import { GetDatasetByIdUseCase } from "@/v1/domain/usecases/get-dataset-by-id-use.case";
import { FeedbackRepository } from "@/v1/infrastructure/FeedbackRepository";

export const loadDependencyContainer = (context: Context) => {
  const useAxios = () => context.$axios;
  const useStore = () => context.store;

  const dependencies: Registration[] = [
    register(DatasetRepository).withDependency(useAxios).and(useStore).build(),

    register(GetDatasetsUseCase)
      .withDependency(DatasetRepository)
      .and(useDatasets)
      .build(),

    register(GetDatasetByIdUseCase)
      .withDependency(DatasetRepository)
      .and(useDataset)
      .build(),

    register(FeedbackRepository).withDependency(useAxios).build(),
  ];

  Container.register(dependencies);
};
