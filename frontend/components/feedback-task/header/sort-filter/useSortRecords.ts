import { useRoute } from "@nuxtjs/composition-api";
import { ref } from "vue-demi";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { MetadataSortList } from "~/v1/domain/entities/metadata/MetadataSort";

export const useSortRecords = ({ metadata }: { metadata: Metadata[] }) => {
  const router = useRoute();
  const metadataSort = ref<MetadataSortList>(new MetadataSortList(metadata));

  const completeByRouteParams = () => {
    if (!metadataSort.value) return;

    metadataSort.value.completeByRouteParams(
      router.value.query._sort as string
    );
  };

  return { metadataSort, completeByRouteParams };
};
