import { ref } from "vue-demi";
import { Metadata } from "~/v1/domain/entities/metadata/Metadata";
import { MetadataSortList } from "~/v1/domain/entities/metadata/MetadataSort";

export const useSortRecords = ({ metadata }: { metadata: Metadata[] }) => {
  const metadataSort = ref<MetadataSortList>(new MetadataSortList(metadata));

  return { metadataSort };
};
