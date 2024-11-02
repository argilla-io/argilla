import { computed } from "vue-demi";
import { useDataset } from "@/v1/infrastructure/storage/DatasetStorage";

export const useAnnotationGuidelinesViewModel = () => {
  const { state: dataset } = useDataset();
  const guidelines = computed(() => dataset.guidelines);

  return {
    guidelines,
  };
};
