import { useResolve } from "ts-injecty";
import { Field } from "~/v1/domain/entities/field/Field";
import { UpdateFieldSettingUseCase } from "~/v1/domain/usecases/dataset-setting/update-field-setting-use-case";

export const useSettingsFieldsViewModel = () => {
  const updateFieldSettingsUseCase = useResolve(UpdateFieldSettingUseCase);

  const restore = (field: Field) => {
    field.restore();
  };

  const update = async (field: Field) => {
    try {
      await updateFieldSettingsUseCase.execute(field);
    } catch (error) {
      // TODO
    }
  };

  return {
    restore,
    update,
  };
};
