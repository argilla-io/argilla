import { useResolve } from "ts-injecty";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { UpdateMetadataSettingUseCase } from "~/v1/domain/usecases/dataset-setting/update-metadata-setting-use-case";

export const useSettingsMetadataViewModel = () => {
  const updateMetadataSetting = useResolve(UpdateMetadataSettingUseCase);

  const restore = (metadata: Metadata) => {
    metadata.restore();
  };

  const update = async (metadata: Metadata) => {
    await updateMetadataSetting.execute(metadata);
  };

  return {
    restore,
    update,
  };
};
