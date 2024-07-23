import { useResolve } from "ts-injecty";
import { UpdateDatasetSettingUseCase } from "~/v1/domain/usecases/dataset-setting/update-dataset-setting-use-case";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";

export const useSettingInfoViewModel = () => {
  const updateDatasetSettingUseCase = useResolve(UpdateDatasetSettingUseCase);

  const update = async (
    dataset: Dataset,
    part: "guidelines" | "metadata" | "distribution"
  ) => {
    try {
      await updateDatasetSettingUseCase.execute(dataset, part);
    } catch (error) {
      // TODO
    }
  };

  return {
    update,
  };
};
