import { DatasetSetting } from "../../entities/DatasetSetting";
import { Field } from "../../entities/field/Field";
import { Question } from "../../entities/question/Question";
import { Vector } from "../../entities/vector/Vector";
import { IDatasetRepository } from "../../services/IDatasetRepository";
import { IDatasetSettingStorage } from "../../services/IDatasetSettingStorage";
import {
  FieldRepository,
  QuestionRepository,
  VectorRepository,
} from "~/v1/infrastructure/repositories";

export class GetDatasetSettingsUseCase {
  constructor(
    private readonly datasetRepository: IDatasetRepository,
    private readonly questionRepository: QuestionRepository,
    private readonly fieldRepository: FieldRepository,
    private readonly vectorRepository: VectorRepository,
    private readonly datasetSettingStorage: IDatasetSettingStorage
  ) {}

  async execute(datasetId: string): Promise<void> {
    const getDataset = this.datasetRepository.getById(datasetId);
    const getQuestions = this.questionRepository.getQuestions(datasetId);
    const getFields = this.fieldRepository.getFields(datasetId);
    const getVectors = this.vectorRepository.getVectors(datasetId);

    const [dataset, backendQuestions, backendFields, backendVectors] =
      await Promise.all([getDataset, getQuestions, getFields, getVectors]);

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

    const datasetSetting = new DatasetSetting(
      dataset,
      questions,
      fields,
      vectors
    );

    this.datasetSettingStorage.save(datasetSetting);
  }
}
