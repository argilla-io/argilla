import { useRoute } from "@nuxtjs/composition-api";
import { ref } from "vue-demi";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { MetadataSortList } from "~/v1/domain/entities/metadata/MetadataSort";
import { useFeatureToggle } from "~/v1/infrastructure/services";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";

export const useSortRecords = ({ metadata }: { metadata: Metadata[] }) => {
  const { getValue } = useFeatureToggle();

  const debounce = useDebounce(getValue("sort-delay", "integer") ?? 500);
  const router = useRoute();
  const metadataSort = ref<MetadataSortList>(new MetadataSortList(metadata));

  const completeByRouteParams = () => {
    if (!metadataSort.value) return;

    metadataSort.value.completeByRouteParams(
      router.value.query._sort as string
    );
  };

  return { metadataSort, completeByRouteParams, debounce };
};
