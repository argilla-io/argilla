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
import { useDatasetSetting } from "@/v1/infrastructure/storage/DatasetSettingStorage";

import { GetDatasetsUseCase } from "@/v1/domain/usecases/get-datasets-use-case";
import { GetDatasetByIdUseCase } from "@/v1/domain/usecases/get-dataset-by-id-use-case";
import { DeleteDatasetUseCase } from "@/v1/domain/usecases/delete-dataset-use-case";
import { GetRecordsToAnnotateUseCase } from "~/v1/domain/usecases/get-records-to-annotate-use-case";
import { SubmitRecordUseCase } from "@/v1/domain/usecases/submit-record-use-case";
import { SaveDraftRecord } from "@/v1/domain/usecases/save-draft-use-case";
import { ClearRecordUseCase } from "@/v1/domain/usecases/clear-record-use-case";
import { DiscardRecordUseCase } from "@/v1/domain/usecases/discard-record-use-case";
import { GetUserMetricsUseCase } from "@/v1/domain/usecases/get-user-metrics-use-case";
import { GetDatasetSettingsUseCase } from "@/v1/domain/usecases/dataset-setting/get-dataset-settings-use-case";
import { UpdateQuestionSettingUseCase } from "@/v1/domain/usecases/dataset-setting/update-question-setting-use-case";
import { UpdateFieldSettingUseCase } from "@/v1/domain/usecases/dataset-setting/update-field-setting-use-case";
import { UpdateDatasetSettingUseCase } from "@/v1/domain/usecases/dataset-setting/update-dataset-setting-use-case";
import { getVectorModelPrimaryKey } from "~/models/Vector";
import { GetDatasetVectorsUseCase } from "../domain/usecases/get-dataset-vectors-use-case";

export const loadDependencyContainer = (context: Context) => {
  const useAxios = () => context.$axios;
  const useStore = () => context.store;

  const dependencies = [
    register(DatasetRepository).withDependencies(useAxios, useStore).build(),
    register(RecordRepository).withDependency(useAxios).build(),
    register(QuestionRepository).withDependency(useAxios).build(),
    register(FieldRepository).withDependency(useAxios).build(),
    register(MetricsRepository).withDependency(useAxios).build(),

    register(DeleteDatasetUseCase).withDependency(DatasetRepository).build(),

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

    register(SaveDraftRecord).withDependency(RecordRepository).build(),

    register(GetDatasetSettingsUseCase)
      .withDependencies(
        DatasetRepository,
        QuestionRepository,
        FieldRepository,
        useDatasetSetting
      )
      .build(),

    register(UpdateQuestionSettingUseCase)
      .withDependency(QuestionRepository)
      .build(),

    register(UpdateFieldSettingUseCase).withDependency(FieldRepository).build(),

    register(UpdateDatasetSettingUseCase)
      .withDependency(DatasetRepository)
      .build(),
    register(GetDatasetVectorsUseCase).build(),
  ];

  Container.register(dependencies);
};
