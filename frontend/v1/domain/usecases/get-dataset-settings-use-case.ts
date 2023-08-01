import { DatasetSetting } from "../entities/DatasetSetting";
import { IDatasetRepository } from "../services/IDatasetRepository";
import { IDatasetSettingStorage } from "../services/IDatasetSettingStorage";
import {
  FieldRepository,
  QuestionRepository,
} from "~/v1/infrastructure/repositories";

export class GetDatasetSettingsUseCase {
  constructor(
    private readonly datasetRepository: IDatasetRepository,
    private readonly questionRepository: QuestionRepository,
    private readonly fieldRepository: FieldRepository,
    private readonly datasetSettingStorage: IDatasetSettingStorage
  ) {}

  async execute(datasetId: string): Promise<void> {
    const getDataset = this.datasetRepository.getById(datasetId);
    const getQuestions = this.questionRepository.getQuestions(datasetId);
    const getFields = this.fieldRepository.getFields(datasetId);

    const [dataset, questions, fields] = await Promise.all([
      getDataset,
      getQuestions,
      getFields,
    ]);

    const datasetSetting = new DatasetSetting(dataset, questions, fields);

    this.datasetSettingStorage.save(datasetSetting);
  }
}
