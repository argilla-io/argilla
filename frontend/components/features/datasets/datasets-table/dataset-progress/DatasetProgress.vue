<template>
  <p v-if="$fetchState.pending">Loading</p>
  <div v-else-if="!!progress" class="dataset-progress">
    <BaseLinearProgress
      class="dataset-progress__bar"
      :progress-ranges="progressRanges"
      :progress-max="progress.total"
      :show-tooltip="true"
    />
    <p class="dataset-progress__pending-info">
      {{ progress.remaining }} {{ $t("left") }}
    </p>
  </div>
</template>

<script>
import { useDatasetProgressViewModel } from "./useDatasetProgressViewModel";

export default {
  props: {
    dataset: {
      type: Object,
    },
  },
  setup(props) {
    return useDatasetProgressViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.dataset-progress {
  display: flex;
  align-items: center;
  gap: $base-space;
  :deep(.submitted) {
    .progress__tooltip__percent-info {
      color: $submitted-color;
    }
  }
  :deep(.discarded) {
    .progress__tooltip__percent-info {
      color: darken($discarded-color, 5%);
    }
  }
  &__bar {
    flex: 1;
    max-width: 180px;
  }
  &__pending-info {
    font-weight: 600;
    color: $black-87;
    @include font-size(12px);
  }
}
</style>
