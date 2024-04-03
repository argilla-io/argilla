<template>
  <div class="dataset-progress">
    <BaseLinearProgress
      class="dataset-progress__bar"
      :progress-ranges="progressRanges"
      :progress-max="totalRecords"
      :show-tooltip="true"
    >
      <template v-slot:tooltip>
        {{ numberOfNonPendingRecords }}/{{ totalRecords }}
      </template>
    </BaseLinearProgress>
    <p class="dataset-progress__pending-info">
      {{ numberOfPendingRecords }} {{ $t("left") }}
    </p>
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
    numberOfPendingRecords() {
      return this.progressRanges.find((range) => range.id === "pending").value;
    },
    numberOfNonPendingRecords() {
      return this.totalRecords - this.numberOfPendingRecords;
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
