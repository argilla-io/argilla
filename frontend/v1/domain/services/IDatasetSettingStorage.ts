import { DatasetSetting } from "../entities/dataset/DatasetSetting";

export interface IDatasetSettingStorage {
  save(dataset: DatasetSetting): void;
}
