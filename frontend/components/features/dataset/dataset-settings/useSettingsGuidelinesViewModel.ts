import { useResolve } from "ts-injecty";
import { UpdateGuidelinesSettingUseCase } from "~/v1/domain/usecases/dataset-setting/update-guidelines-setting-use-case";
import { Dataset } from "~/v1/domain/entities/Dataset";

export const useSettingsGuidelinesViewModel = () => {
  const updateGuidelinesSettingsUseCase = useResolve(
    UpdateGuidelinesSettingUseCase
  );

  const restoreGuidelines = (dataset: Dataset) => {
    dataset.restoreGuidelines();
  };

  const updateGuidelines = async (datasetId: string, newGuidelines: string) => {
    try {
      await updateGuidelinesSettingsUseCase.execute(datasetId, newGuidelines);
    } catch (error) {
      // TODO
    }
  };

  return {
    restoreGuidelines,
    updateGuidelines,
  };
};
