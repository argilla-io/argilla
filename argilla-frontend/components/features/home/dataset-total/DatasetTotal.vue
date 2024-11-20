<template>
  <div class="dataset-total">
    <template v-if="!!totalRecords">
      <svgicon
        name="records"
        height="12"
        width="12"
        color="var(--fg-tertiary)"
        aria-hidden="true"
      />
      <span v-text="`${totalRecords} ${$t('rows')}`" />
    </template>
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
.dataset-total {
  position: relative;
  min-height: 20px;
  display: flex;
  align-items: center;
  gap: calc($base-space / 2);
  color: var(--fg-secondary);
  font-weight: 200;
  @include font-size(12px);
}
</style>
./useDatasetTotalViewModel
