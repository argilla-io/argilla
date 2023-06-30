import { Context } from "@nuxt/types";
import Container, { register } from "ts-injecty";
import { Registration } from "ts-injecty/types";
import { DatasetRepository } from "../infrastructure/DatasetRepository";
import { GetDatasetsUseCase } from "../domain/usecases/get-datasets-use-case";
import { useDatasets } from "../infrastructure/DatasetsStorage";
import { useDataset } from "../infrastructure/DatasetStorage";
import { GetDatasetByIdUseCase } from "../domain/usecases/get-dataset-by-id-use.case";

export const loadDependencyContainer = (context: Context) => {
  const dependencies: Registration[] = [
    register("axios")
      .withImplementation(() => context.$axios)
      .build(),

    register("store")
      .withImplementation(() => context.store)
      .build(),

    register(DatasetRepository).withDependency("axios").and("store").build(),

    register(useDatasets.name)
      .withDynamic(() => useDatasets())
      .build(),
    register(useDataset.name)
      .withDynamic(() => useDataset())
      .build(),

    register(GetDatasetsUseCase)
      .withDependency(DatasetRepository)
      .and(useDatasets.name)
      .build(),

    register(GetDatasetByIdUseCase)
      .withDependency(DatasetRepository)
      .and(useDataset.name)
      .build(),
  ];

  Container.register(dependencies);
};
