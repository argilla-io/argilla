import { useRoute } from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { MetadataFilter } from "~/v1/domain/entities/metadata/MetadataFilter";
import { GetMetadataFiltersUseCase } from "~/v1/domain/usecases/get-metadata-filters-use-case";

export const useMetadataFilterViewModel = () => {
  const router = useRoute();
  const metadataFilters = ref<MetadataFilter>();
  const filterMetaDataUseCase = useResolve(GetMetadataFiltersUseCase);

  const getMetadataFilters = async (datasetId: string) => {
    metadataFilters.value = await filterMetaDataUseCase.execute(datasetId);
  };

  const completeByRouteParams = () => {
    if (!metadataFilters.value) return;

    metadataFilters.value.completeByRouteParams(
      router.value.query._metadata as string
    );
  };

  return { metadataFilters, getMetadataFilters, completeByRouteParams };
};
