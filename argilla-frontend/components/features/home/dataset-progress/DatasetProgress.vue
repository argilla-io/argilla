<template>
  <div class="dataset-progress">
    <p class="dataset-progress__title">{{ $t("metrics.progress.team") }}</p>
    <p class="dataset-progress__percent">{{ getPercent }}%</p>
  </div>
</template>

<script>
import { useDatasetProgressViewModel } from "./useDatasetProgressViewModel";

export default {
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  computed: {
    getPercent() {
      const percent = !!this.progress
        ? this.progress.percentage.completed
        : NaN;
      return isNaN(percent) ? "-" : percent;
    },
  },
  setup(props) {
    return useDatasetProgressViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.dataset-progress {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: calc($base-space / 2);
  max-width: 160px;
  z-index: 0;
  &__title {
    margin: 0;
    @include font-size(12px);
  }
  &__percent {
    margin: 0;
    font-weight: 500;
    color: var(--fg-primary);
    @include font-size(18px);
  }
}
</style>
