<template>
  <BaseLinearProgressSkeleton v-if="!isLoaded" class="dataset-progress__bar" />
  <transition v-else-if="!!progress" name="fade" appear>
    <div class="dataset-progress">
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
    datasetId: {
      type: String,
      required: true,
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
}
</style>
