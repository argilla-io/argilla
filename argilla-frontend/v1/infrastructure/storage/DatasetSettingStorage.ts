import { useStoreFor } from "@/v1/store/create";
import { DatasetSetting } from "~/v1/domain/entities/dataset/DatasetSetting";
import { IDatasetSettingStorage } from "~/v1/domain/services/IDatasetSettingStorage";

const useStoreForDatasetSetting = useStoreFor<
  DatasetSetting,
  IDatasetSettingStorage
>(DatasetSetting);
export const useDatasetSetting = () => useStoreForDatasetSetting();
