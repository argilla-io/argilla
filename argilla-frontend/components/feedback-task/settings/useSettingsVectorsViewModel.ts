import { useResolve } from "ts-injecty";
import { Vector } from "~/v1/domain/entities/vector/Vector";
import { UpdateVectorSettingUseCase } from "~/v1/domain/usecases/dataset-setting/update-vector-setting-use-case";

export const useSettingsVectorsViewModel = () => {
  const updateVectorUseCase = useResolve(UpdateVectorSettingUseCase);

  const restore = (vector: Vector) => {
    vector.restore();
  };

  const update = async (vector: Vector) => {
    await updateVectorUseCase.execute(vector);
  };

  return {
    restore,
    update,
  };
};
