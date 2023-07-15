import { Context } from "@nuxt/types";
import Container, { register } from "ts-injecty";
import { Registration } from "ts-injecty/types";

import { useEventDispatcher } from "@codescouts/events";
import { useMetrics } from "../infrastructure/storage/MetricsStorage";
import {
  DatasetRepository,
  RecordRepository,
  QuestionRepository,
  FieldRepository,
  MetricsRepository,
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
import { GetUserMetricsUseCase } from "@/v1/domain/usecases/get-user-metrics-use-case";

export const loadDependencyContainer = (context: Context) => {
  const useAxios = () => context.$axios;
  const useStore = () => context.store;

  const dependencies: Registration[] = [
    register(DatasetRepository).withDependency(useAxios).and(useStore).build(),
    register(RecordRepository).withDependency(useAxios).build(),
    register(QuestionRepository).withDependency(useAxios).build(),
    register(FieldRepository).withDependency(useAxios).build(),
    register(MetricsRepository).withDependency(useAxios).build(),

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

    register(DiscardRecordUseCase)
      .withDependency(RecordRepository)
      .and(useEventDispatcher)
      .build(),
    register(SubmitRecordUseCase)
      .withDependency(RecordRepository)
      .and(useEventDispatcher)
      .build(),
    register(ClearRecordUseCase)
      .withDependency(RecordRepository)
      .and(useEventDispatcher)
      .build(),

    register(GetUserMetricsUseCase)
      .withDependency(MetricsRepository)
      .and(useMetrics)
      .build(),
  ];

  Container.register(dependencies);
};
