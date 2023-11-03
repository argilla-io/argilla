import { DatasetSetting } from "../../entities/DatasetSetting";
import { Field } from "../../entities/field/Field";
import { Metadata } from "../../entities/metadata/Metadata";
import { Question } from "../../entities/question/Question";
import { Vector } from "../../entities/vector/Vector";
import { IDatasetRepository } from "../../services/IDatasetRepository";
import { IDatasetSettingStorage } from "../../services/IDatasetSettingStorage";
import { RoleService } from "../../services/RoleService";
import {
  FieldRepository,
  MetadataRepository,
  QuestionRepository,
  VectorRepository,
} from "~/v1/infrastructure/repositories";

export class GetDatasetSettingsUseCase {
  constructor(
    private readonly roleService: RoleService,
    private readonly datasetRepository: IDatasetRepository,
    private readonly questionRepository: QuestionRepository,
    private readonly fieldRepository: FieldRepository,
    private readonly vectorRepository: VectorRepository,
    private readonly metadataRepository: MetadataRepository,
    private readonly datasetSettingStorage: IDatasetSettingStorage
  ) {}

  async execute(datasetId: string): Promise<DatasetSetting> {
    const isAdminOrRole = this.roleService.isAdminOrOwner();

    const datasetSetting = isAdminOrRole
      ? await this.createDatasetSettingsForAdminOrOwner(datasetId)
      : await this.createDatasetSettingsForAnnotator(datasetId);

    this.datasetSettingStorage.save(datasetSetting);

    return datasetSetting;
  }

  private async createDatasetSettingsForAnnotator(
    datasetId: string
  ): Promise<DatasetSetting> {
    const dataset = await this.datasetRepository.getById(datasetId);

    return new DatasetSetting(dataset);
  }

  private async createDatasetSettingsForAdminOrOwner(
    datasetId: string
  ): Promise<DatasetSetting> {
    const getDataset = this.datasetRepository.getById(datasetId);
    const getQuestions = this.questionRepository.getQuestions(datasetId);
    const getFields = this.fieldRepository.getFields(datasetId);
    const getVectors = this.vectorRepository.getVectors(datasetId);
    const getMetadataProperties =
      this.metadataRepository.getMetadataFilters(datasetId);

    const [
      dataset,
      backendQuestions,
      backendFields,
      backendVectors,
      backendMetadataProperties,
    ] = await Promise.all([
      getDataset,
      getQuestions,
      getFields,
      getVectors,
      getMetadataProperties,
    ]);

    const questions = backendQuestions.map((question) => {
      return new Question(
        question.id,
        question.name,
        question.description,
        datasetId,
        question.title,
        question.required,
        question.settings
      );
    });

    const fields = backendFields.map((field) => {
      return new Field(
        field.id,
        field.name,
        field.title,
        "",
        datasetId,
        field.required,
        field.settings
      );
    });

    const vectors = backendVectors.map((vector) => {
      return new Vector(
        vector.id,
        vector.name,
        vector.title,
        vector.dimensions
      );
    });

    const metadataProperties = backendMetadataProperties.map((metadata) => {
      return new Metadata(
        metadata.id,
        metadata.name,
        metadata.title,
        metadata.settings,
        metadata.visible_for_annotators
      );
    });

    return new DatasetSetting(
      dataset,
      questions,
      fields,
      vectors,
      metadataProperties
    );
  }
}
