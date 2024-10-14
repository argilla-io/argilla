import { Context } from "@nuxt/types";
import Container, { register } from "ts-injecty";

import { useEventDispatcher } from "@codescouts/events";

import { useTeamProgress } from "../infrastructure/storage/TeamProgressStorage";
import {
  UpdateMetricsEventHandler,
  UpdateTeamProgressEventHandler,
} from "../infrastructure/events";
import { LoadUserUseCase } from "../domain/usecases/load-user-use-case";
import { CreateDatasetUseCase } from "../domain/usecases/create-dataset-use-case";
import { useAxiosExtension } from "@/v1/infrastructure/services/useAxiosExtension";

import {
  DatasetRepository,
  RecordRepository,
  QuestionRepository,
  FieldRepository,
  MetricsRepository,
  MetadataRepository,
  VectorRepository,
  AgentRepository,
  OAuthRepository,
  EnvironmentRepository,
  WorkspaceRepository,
  AuthRepository,
  UserRepository,
  HubRepository,
} from "@/v1/infrastructure/repositories";

import { useRole, useRoutes } from "@/v1/infrastructure/services";
import { useDataset } from "@/v1/infrastructure/storage/DatasetStorage";
import { useRecords } from "@/v1/infrastructure/storage/RecordsStorage";
import { useDatasets } from "@/v1/infrastructure/storage/DatasetsStorage";
import { useMetrics } from "@/v1/infrastructure/storage/MetricsStorage";
import { useDatasetSetting } from "@/v1/infrastructure/storage/DatasetSettingStorage";

import { GetDatasetCreationUseCase } from "@/v1/domain/usecases/get-dataset-creation-use-case";
import { GetDatasetsUseCase } from "@/v1/domain/usecases/get-datasets-use-case";
import { GetDatasetByIdUseCase } from "@/v1/domain/usecases/get-dataset-by-id-use-case";
import { GetDatasetProgressUseCase } from "@/v1/domain/usecases/get-dataset-progress-use-case";
import { DeleteDatasetUseCase } from "@/v1/domain/usecases/delete-dataset-use-case";
import { GetRecordsByCriteriaUseCase } from "@/v1/domain/usecases/get-records-by-criteria-use-case";
import { LoadRecordsToAnnotateUseCase } from "@/v1/domain/usecases/load-records-to-annotate-use-case";
import { GetFieldsUseCase } from "@/v1/domain/usecases/get-fields-use-case";
import { SubmitRecordUseCase } from "@/v1/domain/usecases/submit-record-use-case";
import { SaveDraftUseCase } from "@/v1/domain/usecases/save-draft-use-case";
import { BulkAnnotationUseCase } from "@/v1/domain/usecases/bulk-annotation-use-case";
import { DiscardRecordUseCase } from "@/v1/domain/usecases/discard-record-use-case";
import { GetUserMetricsUseCase } from "@/v1/domain/usecases/get-user-metrics-use-case";
import { GetDatasetSettingsUseCase } from "@/v1/domain/usecases/dataset-setting/get-dataset-settings-use-case";
import { UpdateQuestionSettingUseCase } from "@/v1/domain/usecases/dataset-setting/update-question-setting-use-case";
import { UpdateFieldSettingUseCase } from "@/v1/domain/usecases/dataset-setting/update-field-setting-use-case";
import { UpdateDatasetSettingUseCase } from "@/v1/domain/usecases/dataset-setting/update-dataset-setting-use-case";
import { GetMetadataUseCase } from "@/v1/domain/usecases/get-metadata-use-case";
import { GetDatasetVectorsUseCase } from "@/v1/domain/usecases/get-dataset-vectors-use-case";
import { UpdateVectorSettingUseCase } from "@/v1/domain/usecases/dataset-setting/update-vector-setting-use-case";
import { GetDatasetQuestionsFilterUseCase } from "@/v1/domain/usecases/get-dataset-questions-filter-use-case";
import { GetDatasetSuggestionsAgentsUseCase } from "@/v1/domain/usecases/get-dataset-suggestions-agents-use-case";
import { UpdateMetadataSettingUseCase } from "@/v1/domain/usecases/dataset-setting/update-metadata-setting-use-case";
import { OAuthLoginUseCase } from "@/v1/domain/usecases/oauth-login-use-case";
import { GetEnvironmentUseCase } from "@/v1/domain/usecases/get-environment-use-case";
import { GetWorkspacesUseCase } from "@/v1/domain/usecases/get-workspaces-use-case";
import { GetDatasetQuestionsGroupedUseCase } from "@/v1/domain/usecases/get-dataset-questions-grouped-use-case";
import { AuthLoginUseCase } from "@/v1/domain/usecases/auth-login-use-case";

export const loadDependencyContainer = (context: Context) => {
  const useAxios = useAxiosExtension(() => context.$axios);
  const useAuth = () => context.$auth;

  const dependencies = [
    register(UpdateMetricsEventHandler).build(),
    register(UpdateTeamProgressEventHandler).build(),
    register(HubRepository).withDependency(useAxios).build(),
    register(DatasetRepository).withDependency(useAxios).build(),
    register(RecordRepository).withDependency(useAxios).build(),
    register(QuestionRepository).withDependency(useAxios).build(),
    register(FieldRepository).withDependency(useAxios).build(),
    register(MetricsRepository).withDependency(useAxios).build(),
    register(MetadataRepository).withDependency(useAxios).build(),
    register(VectorRepository).withDependency(useAxios).build(),
    register(AgentRepository).withDependency(useAxios).build(),
    register(WorkspaceRepository).withDependency(useAxios).build(),

    register(OAuthRepository).withDependencies(useAxios, useRoutes).build(),
    register(EnvironmentRepository).withDependency(useAxios).build(),
    register(AuthRepository).withDependency(useAxios).build(),
    register(UserRepository).withDependency(useAxios).build(),

    register(GetDatasetCreationUseCase).withDependency(HubRepository).build(),

    register(DeleteDatasetUseCase).withDependency(DatasetRepository).build(),

    register(GetWorkspacesUseCase).withDependency(WorkspaceRepository).build(),

    register(GetDatasetsUseCase)
      .withDependencies(DatasetRepository, useDatasets)
      .build(),

    register(GetDatasetByIdUseCase)
      .withDependencies(DatasetRepository, useDataset)
      .build(),

    register(GetDatasetProgressUseCase)
      .withDependencies(DatasetRepository, useTeamProgress)
      .build(),

    register(GetRecordsByCriteriaUseCase)
      .withDependencies(
        RecordRepository,
        QuestionRepository,
        FieldRepository,
        useRecords
      )
      .build(),

    register(GetUserMetricsUseCase)
      .withDependencies(MetricsRepository, useMetrics)
      .build(),

    register(LoadRecordsToAnnotateUseCase)
      .withDependencies(
        GetRecordsByCriteriaUseCase,
        GetDatasetProgressUseCase,
        GetUserMetricsUseCase,
        useRecords
      )
      .build(),

    register(GetFieldsUseCase).withDependency(FieldRepository).build(),

    register(DiscardRecordUseCase)
      .withDependencies(RecordRepository, useEventDispatcher)
      .build(),

    register(SubmitRecordUseCase)
      .withDependencies(RecordRepository, useEventDispatcher)
      .build(),

    register(SaveDraftUseCase)
      .withDependencies(RecordRepository, useEventDispatcher)
      .build(),

    register(BulkAnnotationUseCase)
      .withDependencies(
        GetRecordsByCriteriaUseCase,
        LoadRecordsToAnnotateUseCase,
        RecordRepository,
        useEventDispatcher
      )
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

    register(GetDatasetQuestionsGroupedUseCase)
      .withDependency(QuestionRepository)
      .build(),

    register(GetDatasetSuggestionsAgentsUseCase)
      .withDependency(AgentRepository)
      .build(),

    register(GetEnvironmentUseCase)
      .withDependency(EnvironmentRepository)
      .build(),

    register(LoadUserUseCase).withDependencies(useAuth, UserRepository).build(),

    register(OAuthLoginUseCase)
      .withDependencies(useAuth, OAuthRepository, LoadUserUseCase)
      .build(),

    register(AuthLoginUseCase)
      .withDependencies(useAuth, AuthRepository, LoadUserUseCase)
      .build(),

    register(CreateDatasetUseCase)
      .withDependencies(
        DatasetRepository,
        WorkspaceRepository,
        QuestionRepository,
        FieldRepository
      )
      .build(),
  ];

  Container.register(dependencies);
};
