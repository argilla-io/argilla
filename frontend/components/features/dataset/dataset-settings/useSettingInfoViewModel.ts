import { useResolve } from "ts-injecty";
import { UpdateGuidelinesSettingUseCase } from "~/v1/domain/usecases/dataset-setting/update-guidelines-setting-use-case";
import { Dataset } from "~/v1/domain/entities/Dataset";

export const useSettingInfoViewModel = () => {
  const updateGuidelinesSettingsUseCase = useResolve(
    UpdateGuidelinesSettingUseCase
  );

  const restore = (dataset: Dataset) => {
    dataset.restore();
  };

  const updateGuidelines = async (dataset: Dataset) => {
    try {
      await updateGuidelinesSettingsUseCase.execute(dataset);
    } catch (error) {
      // TODO
    }
  };

  return {
    restore,
    updateGuidelines,
  };
};
