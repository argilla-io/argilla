import { useResolve } from "ts-injecty";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { UpdateDatasetSettingUseCase } from "~/v1/domain/usecases/dataset-setting/update-dataset-setting-use-case";
import { UpdateMetadataSettingUseCase } from "~/v1/domain/usecases/dataset-setting/update-metadata-setting-use-case";

export const useSettingsMetadataViewModel = () => {
  const updateMetadataSetting = useResolve(UpdateMetadataSettingUseCase);
  const updateDatasetSetting = useResolve(UpdateDatasetSettingUseCase);

  const restore = (metadata: Metadata) => {
    metadata.restore();
  };

  const updateMetadata = async (metadata: Metadata) => {
    await updateMetadataSetting.execute(metadata);
  };

  const updateDataset = async (dataset: Dataset) => {
    await updateDatasetSetting.execute(dataset, "metadata");
  };

  return {
    restore,
    updateMetadata,
    updateDataset,
  };
};
