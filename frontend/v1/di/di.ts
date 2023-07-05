import { Context } from "@nuxt/types";
import Container, { register } from "ts-injecty";
import { Registration } from "ts-injecty/types";
import { DatasetRepository } from "../infrastructure/DatasetRepository";
import { GetDatasetsUseCase } from "../domain/usecases/get-datasets-use-case";
import { useDatasets } from "../infrastructure/DatasetsStorage";
import { useDataset } from "../infrastructure/DatasetStorage";
import { GetDatasetByIdUseCase } from "../domain/usecases/get-dataset-by-id-use.case";

export const loadDependencyContainer = (context: Context) => {
  const useAxios = () => context.$axios;
  const useStore = () => context.store;
  const dependencies: Registration[] = [
    register("axios").withImplementation(useAxios).build(),
    register("store").withImplementation(useStore).build(),

    register(DatasetRepository).withDependency("axios").and("store").build(),

    register(GetDatasetsUseCase)
      .withDependency(DatasetRepository)
      .and(useDatasets)
      .build(),

    register(GetDatasetByIdUseCase)
      .withDependency(DatasetRepository)
      .and(useDataset)
      .build(),
  ];

  Container.register(dependencies);
};
