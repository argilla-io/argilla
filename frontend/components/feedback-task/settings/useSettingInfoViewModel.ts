import { useResolve } from "ts-injecty";
import { UpdateDatasetSettingUseCase } from "~/v1/domain/usecases/dataset-setting/update-dataset-setting-use-case";
import { Dataset } from "~/v1/domain/entities/Dataset";

export const useSettingInfoViewModel = () => {
  const updateDatasetSettingUseCase = useResolve(UpdateDatasetSettingUseCase);

  const restore = (dataset: Dataset) => {
    dataset.restore();
  };

  const update = async (dataset: Dataset) => {
    try {
      await updateDatasetSettingUseCase.execute(dataset);
    } catch (error) {
      // TODO
    }
  };

  return {
    restore,
    update,
  };
};
