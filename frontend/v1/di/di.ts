import { Context } from "@nuxt/types";
import Container, { register } from "ts-injecty";
import { Registration } from "ts-injecty/types";

import {
  DatasetRepository,
  RecordRepository,
  QuestionRepository,
  FieldRepository,
} from "@/v1/infrastructure/repositories";

import { useDataset } from "@/v1/infrastructure/storage/DatasetStorage";
import { useRecords } from "@/v1/infrastructure/storage/RecordsStorage";
import { useDatasets } from "@/v1/infrastructure/storage/DatasetsStorage";

import { GetDatasetsUseCase } from "@/v1/domain/usecases/get-datasets-use-case";
import { GetDatasetByIdUseCase } from "@/v1/domain/usecases/get-dataset-by-id-use-case";
import { GetRecordsForAnnotateUseCase } from "@/v1/domain/usecases/get-records-for-annotate-use-case";
import { SubmitRecordUseCase } from "@/v1/domain/usecases/submit-record-use-case";
import { ClearRecordUseCase } from "@/v1/domain/usecases/clear-record-use-case";
import { DiscardRecordUseCase } from "@/v1/domain/usecases/discard-record-use-case";

export const loadDependencyContainer = (context: Context) => {
  const useAxios = () => context.$axios;
  const useStore = () => context.store;

  const dependencies: Registration[] = [
    register(DatasetRepository).withDependency(useAxios).and(useStore).build(),
    register(RecordRepository).withDependency(useAxios).build(),
    register(QuestionRepository).withDependency(useAxios).build(),
    register(FieldRepository).withDependency(useAxios).build(),

    register(GetDatasetsUseCase)
      .withDependency(DatasetRepository)
      .and(useDatasets)
      .build(),

    register(GetDatasetByIdUseCase)
      .withDependency(DatasetRepository)
      .and(useDataset)
      .build(),

    register(GetRecordsForAnnotateUseCase)
      .withDependency(useAxios)
      .and(useRecords)
      .build(),

    register(DiscardRecordUseCase).withDependency(RecordRepository).build(),
    register(SubmitRecordUseCase).withDependency(RecordRepository).build(),
    register(ClearRecordUseCase).withDependency(RecordRepository).build(),
  ];

  Container.register(dependencies);
};
