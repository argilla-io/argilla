import { onBeforeMount } from "vue-demi";
import { useDatasetViewModel } from "./useDatasetViewModel";

export const useDatasetSettingViewModel = () => {
  const datasetViewModel = useDatasetViewModel();

  onBeforeMount(() => {
    datasetViewModel.loadDataset();
  });

  return { ...datasetViewModel };
};
