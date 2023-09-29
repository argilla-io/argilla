import { useRoute } from "@nuxtjs/composition-api";
import { ref } from "vue-demi";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { MetadataFilterList } from "~/v1/domain/entities/metadata/MetadataFilter";

export const useMetadataFilterViewModel = ({
  metadata,
}: {
  metadata: Metadata[];
}) => {
  const router = useRoute();
  const metadataFilters = ref<MetadataFilterList>(
    new MetadataFilterList(metadata)
  );

  const completeByRouteParams = () => {
    if (!metadataFilters.value) return;

    metadataFilters.value.completeByRouteParams(
      router.value.query._metadata as string
    );
  };

  return { metadataFilters, completeByRouteParams };
};
