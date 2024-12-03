import { ref, useFetch } from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";
import { Field } from "~/v1/domain/entities/field/Field";
import { GetDatasetFieldsGroupedUseCase } from "~/v1/domain/usecases/get-dataset-fields-grouped-use-case";

export const useDatasetFields = ({ dataset }: { dataset: Dataset }) => {
  const getFieldsUseCase = useResolve(GetDatasetFieldsGroupedUseCase);
  const fields = ref<Field[]>([]);
  const isFieldsLoading = ref(false);

  useFetch(async () => {
    try {
      isFieldsLoading.value = true;

      fields.value = await getFieldsUseCase.execute(dataset.id);
    } catch {
    } finally {
      isFieldsLoading.value = false;
    }
  });

  return {
    fields,
    isFieldsLoading,
  };
};
