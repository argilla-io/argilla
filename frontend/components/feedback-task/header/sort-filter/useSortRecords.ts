import { ref } from "vue-demi";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { MetadataSortList } from "~/v1/domain/entities/metadata/MetadataSort";
import { useFeatureToggle } from "~/v1/infrastructure/services";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";

export const useSortRecords = ({
  datasetMetadata,
}: {
  datasetMetadata: Metadata[];
}) => {
  const { getValue } = useFeatureToggle();

  const debounce = useDebounce(getValue("sort-delay", "integer") ?? 500);
  const metadataSort = ref<MetadataSortList>(
    new MetadataSortList(datasetMetadata)
  );

  return { metadataSort, debounce };
};
