import { computed, onBeforeMount } from "vue-demi";
import { useDatasetViewModel } from "./useDatasetViewModel";

export const useDatasetSettingViewModel = () => {
  const datasetViewModel = useDatasetViewModel();
  const breadcrumbs = computed(() => {
    return [
      ...datasetViewModel.breadcrumbs.value,
      {
        link: null,
        name: "settings",
      },
    ];
  });

  onBeforeMount(() => {
    datasetViewModel.loadDataset();
  });

  return { ...datasetViewModel, breadcrumbs };
};
