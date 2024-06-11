import { computed } from "@nuxtjs/composition-api";
import { useDataset } from "@/v1/infrastructure/storage/DatasetStorage";

export const useAnnotationGuidelinesViewModel = () => {
  const { state: dataset } = useDataset();

  const guidelines = computed(() => dataset.guidelines || "");

  return {
    guidelines,
  };
};
