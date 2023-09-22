import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { GetMetadataFiltersUseCase } from "~/v1/domain/usecases/get-metadata-filters-use-case";

export const useMetadataFilterViewModel = () => {
  const metadataFilters = ref([]);
  const filterMetaDataUseCase = useResolve(GetMetadataFiltersUseCase);

  const getMetadataFilters = async (datasetId: string) => {
    const filters = await filterMetaDataUseCase.execute(datasetId);

    metadataFilters.value = filters;
  };

  return { metadataFilters, getMetadataFilters };
};
