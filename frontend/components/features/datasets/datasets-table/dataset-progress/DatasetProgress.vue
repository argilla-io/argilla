<template>
  <BaseLinearProgressSkeleton
    v-if="$fetchState.pending"
    class="dataset-progress__bar"
  />
  <transition v-else-if="!!progress" name="fade" appear>
    <div class="dataset-progress">
      <BaseLinearProgress
        class="dataset-progress__bar"
        :progress-ranges="progressRanges"
        :progress-max="progress.total"
        :show-tooltip="true"
      />
      <p class="dataset-progress__pending-info">
        {{ progress.pending }} {{ $t("datasets.left") }}
      </p>
    </div>
  </transition>
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
  gap: $base-space * 2;
  &__bar {
    flex: 1;
    max-width: 160px;
  }
  &__pending-info {
    margin: 0;
    color: $black-54;
    @include font-size(12px);
    font-weight: 500;
  }
}
</style>
