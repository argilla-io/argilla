<template>
  <BaseLinearProgressSkeleton
    v-if="$fetchState.pending"
    class="dataset-progress__bar"
  />
  <transition v-else-if="!!progress" name="fade" appear>
    <div class="dataset-progress">
      <p class="dataset-progress__pending-info">
        {{ progress.pending }} {{ $t("datasets.left") }}
      </p>
      <BaseLinearProgress
        class="dataset-progress__bar"
        :progress-ranges="progressRanges"
        :progress-max="progress.total"
        :show-tooltip="true"
      />
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
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: calc($base-space / 2);
  max-width: 160px;
  z-index: 0;
  &__bar {
    width: 100%;
    max-width: 160px;
  }
  &__pending-info {
    color: $black-37;
    @include font-size(12px);
    margin: 0 0 0 auto;
  }
}
</style>
