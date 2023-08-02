import { Context } from "@nuxt/types";
import Container, { register } from "ts-injecty";

import { useEventDispatcher } from "@codescouts/events";
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
import { useMetrics } from "@/v1/infrastructure/storage/MetricsStorage";

import { GetDatasetsUseCase } from "@/v1/domain/usecases/get-datasets-use-case";
import { GetDatasetByIdUseCase } from "@/v1/domain/usecases/get-dataset-by-id-use-case";
import { GetRecordsToAnnotateUseCase } from "~/v1/domain/usecases/get-records-to-annotate-use-case";
import { SubmitRecordUseCase } from "@/v1/domain/usecases/submit-record-use-case";
import { ClearRecordUseCase } from "@/v1/domain/usecases/clear-record-use-case";
import { DiscardRecordUseCase } from "@/v1/domain/usecases/discard-record-use-case";
import { GetUserMetricsUseCase } from "@/v1/domain/usecases/get-user-metrics-use-case";

export const loadDependencyContainer = (context: Context) => {
  const useAxios = () => context.$axios;
  const useStore = () => context.store;

  const dependencies = [
    register(DatasetRepository).withDependencies(useAxios, useStore).build(),
    register(RecordRepository).withDependency(useAxios).build(),
    register(QuestionRepository).withDependency(useAxios).build(),
    register(FieldRepository).withDependency(useAxios).build(),
    register(MetricsRepository).withDependency(useAxios).build(),

    register(GetDatasetsUseCase)
      .withDependencies(DatasetRepository, useDatasets)
      .build(),

    register(GetDatasetByIdUseCase)
      .withDependencies(DatasetRepository, useDataset)
      .build(),

    register(GetRecordsToAnnotateUseCase)
      .withDependencies(
        RecordRepository,
        QuestionRepository,
        FieldRepository,
        useRecords
      )
      .build(),

    register(DiscardRecordUseCase)
      .withDependencies(RecordRepository, useEventDispatcher)
      .build(),

    register(SubmitRecordUseCase)
      .withDependencies(RecordRepository, useEventDispatcher)
      .build(),

    register(ClearRecordUseCase)
      .withDependencies(RecordRepository, useEventDispatcher)
      .build(),

    register(GetUserMetricsUseCase)
      .withDependencies(MetricsRepository, useMetrics)
      .build(),
  ];

  Container.register(dependencies);
};
