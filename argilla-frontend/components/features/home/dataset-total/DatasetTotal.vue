<template>
  <div v-if="!!totalRecords" class="dataset-progress">
    <svgicon
      name="records"
      height="12"
      width="12"
      color="var(--fg-seconadary)"
    />
    <span v-text="totalRecords" />
  </div>
</template>

<script>
import "assets/icons/records";
import { useDatasetTotalViewModel } from "./useDatasetTotalViewModel";

export default {
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    return useDatasetTotalViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.dataset-progress {
  position: relative;
  display: flex;
  align-items: center;
  gap: calc($base-space / 2);
  color: var(--fg-secondary);
  @include font-size(12px);
}
</style>
./useDatasetTotalViewModel