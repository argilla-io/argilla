import { useRoute } from "@nuxtjs/composition-api";
import { ref } from "vue-demi";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { MetadataFilterList } from "~/v1/domain/entities/metadata/MetadataFilter";
import { useFeatureToggle } from "~/v1/infrastructure/services";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";

export const useMetadataFilterViewModel = ({
  metadata,
}: {
  metadata: Metadata[];
}) => {
  const { getValue } = useFeatureToggle();
  const router = useRoute();
  const debounce = useDebounce(
    getValue("metadata-filter-delay", "integer") ?? 1000
  );
  const metadataFilters = ref<MetadataFilterList>(
    new MetadataFilterList(metadata)
  );

  const completeByRouteParams = () => {
    if (!metadataFilters.value) return;

    metadataFilters.value.completeByRouteParams(
      router.value.query._metadata as string
    );
  };

  return { metadataFilters, completeByRouteParams, debounce };
};
