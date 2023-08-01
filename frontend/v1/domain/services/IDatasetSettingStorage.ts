import { DatasetSetting } from "../entities/DatasetSetting";

export interface IDatasetSettingStorage {
  save(dataset: DatasetSetting): void;
}
