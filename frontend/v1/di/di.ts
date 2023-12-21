import { Context } from "@nuxt/types";
import Container, { register } from "ts-injecty";

import { useEventDispatcher } from "@codescouts/events";

import {
  DatasetRepository,
  RecordRepository,
  QuestionRepository,
  FieldRepository,
  MetricsRepository,
  MetadataRepository,
  VectorRepository,
  AgentRepository,
} from "@/v1/infrastructure/repositories";

import { useRole } from "@/v1/infrastructure/services";
import { useDataset } from "@/v1/infrastructure/storage/DatasetStorage";
import { useRecords } from "@/v1/infrastructure/storage/RecordsStorage";
import { useDatasets } from "@/v1/infrastructure/storage/DatasetsStorage";
import { useMetrics } from "@/v1/infrastructure/storage/MetricsStorage";
import { useDatasetSetting } from "@/v1/infrastructure/storage/DatasetSettingStorage";

import { GetDatasetsUseCase } from "@/v1/domain/usecases/get-datasets-use-case";
import { GetDatasetByIdUseCase } from "@/v1/domain/usecases/get-dataset-by-id-use-case";
import { DeleteDatasetUseCase } from "@/v1/domain/usecases/delete-dataset-use-case";
import { LoadRecordsToAnnotateUseCase } from "@/v1/domain/usecases/load-records-to-annotate-use-case";
import { SubmitRecordUseCase } from "@/v1/domain/usecases/submit-record-use-case";
import { SubmitBulkAnnotationUseCase } from "@/v1/domain/usecases/submit-bulk-annotation-use-case";
import { SaveDraftUseCase } from "@/v1/domain/usecases/save-draft-use-case";
import { SaveDraftBulkAnnotationUseCase } from "@/v1/domain/usecases/save-draft-bulk-annotation-use-case";
import { DiscardRecordUseCase } from "@/v1/domain/usecases/discard-record-use-case";
import { DiscardBulkAnnotationUseCase } from "@/v1/domain/usecases/discard-bulk-annotation-use-case";
import { GetUserMetricsUseCase } from "@/v1/domain/usecases/get-user-metrics-use-case";
import { GetDatasetSettingsUseCase } from "@/v1/domain/usecases/dataset-setting/get-dataset-settings-use-case";
import { UpdateQuestionSettingUseCase } from "@/v1/domain/usecases/dataset-setting/update-question-setting-use-case";
import { UpdateFieldSettingUseCase } from "@/v1/domain/usecases/dataset-setting/update-field-setting-use-case";
import { UpdateDatasetSettingUseCase } from "@/v1/domain/usecases/dataset-setting/update-dataset-setting-use-case";
import { GetMetadataUseCase } from "@/v1/domain/usecases/get-metadata-use-case";
import { GetDatasetVectorsUseCase } from "@/v1/domain/usecases/get-dataset-vectors-use-case";
import { UpdateVectorSettingUseCase } from "@/v1/domain/usecases/dataset-setting/update-vector-setting-use-case";
import { GetDatasetQuestionsFilterUseCase } from "~/v1/domain/usecases/get-dataset-questions-filter-use-case";
import { GetDatasetSuggestionsAgentsUseCase } from "@/v1/domain/usecases/get-dataset-suggestions-agents-use-case";
import { UpdateMetadataSettingUseCase } from "@/v1/domain/usecases/dataset-setting/update-metadata-setting-use-case";

export const loadDependencyContainer = (context: Context) => {
  const useAxios = () => context.$axios;
  const useStore = () => context.store;

  const dependencies = [
    register(DatasetRepository).withDependencies(useAxios, useStore).build(),
    register(RecordRepository).withDependency(useAxios).build(),
    register(QuestionRepository).withDependency(useAxios).build(),
    register(FieldRepository).withDependency(useAxios).build(),
    register(MetricsRepository).withDependency(useAxios).build(),
    register(MetadataRepository).withDependency(useAxios).build(),
    register(VectorRepository).withDependency(useAxios).build(),
    register(AgentRepository).withDependency(useAxios).build(),

    register(DeleteDatasetUseCase).withDependency(DatasetRepository).build(),

    register(GetDatasetsUseCase)
      .withDependencies(DatasetRepository, useDatasets)
      .build(),

    register(GetDatasetByIdUseCase)
      .withDependencies(DatasetRepository, useDataset)
      .build(),

    register(LoadRecordsToAnnotateUseCase)
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

    register(DiscardBulkAnnotationUseCase)
      .withDependencies(RecordRepository, useEventDispatcher)
      .build(),

    register(SubmitRecordUseCase)
      .withDependencies(RecordRepository, useEventDispatcher)
      .build(),

    register(SubmitBulkAnnotationUseCase)
      .withDependencies(RecordRepository, useEventDispatcher)
      .build(),

    register(SaveDraftUseCase)
      .withDependencies(RecordRepository, useEventDispatcher)
      .build(),

    register(SaveDraftBulkAnnotationUseCase)
      .withDependencies(RecordRepository, useEventDispatcher)
      .build(),

    register(GetUserMetricsUseCase)
      .withDependencies(MetricsRepository, useMetrics)
      .build(),

    register(GetDatasetSettingsUseCase)
      .withDependencies(
        useRole,
        DatasetRepository,
        QuestionRepository,
        FieldRepository,
        VectorRepository,
        MetadataRepository,
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

    register(UpdateVectorSettingUseCase)
      .withDependency(VectorRepository)
      .build(),

    register(UpdateMetadataSettingUseCase)
      .withDependency(MetadataRepository)
      .build(),

    register(GetMetadataUseCase).withDependency(MetadataRepository).build(),

    register(GetDatasetVectorsUseCase).withDependency(VectorRepository).build(),

    register(GetDatasetQuestionsFilterUseCase)
      .withDependency(QuestionRepository)
      .build(),

    register(GetDatasetSuggestionsAgentsUseCase)
      .withDependency(AgentRepository)
      .build(),
  ];

  Container.register(dependencies);
};
