import { ref } from "vue-demi";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { MetadataFilterList } from "~/v1/domain/entities/metadata/MetadataFilter";
import { useFeatureToggle } from "~/v1/infrastructure/services";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";

export const useMetadataFilterViewModel = ({
  datasetMetadata,
}: {
  datasetMetadata: Metadata[];
}) => {
  const { getValue } = useFeatureToggle();
  const debounce = useDebounce(
    getValue("metadata-filter-delay", "integer") ?? 500
  );
  const metadataFilters = ref<MetadataFilterList>(
    new MetadataFilterList(datasetMetadata)
  );

  return { metadataFilters, debounce };
};
