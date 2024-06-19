<template>
  <div class="dataset-progress">
    <BaseLinearProgress
      class="dataset-progress__bar"
      :progress-ranges="progressRanges"
      :progress-max="total"
    />
    <span class="dataset-progress__data"
      >{{ progressCompleted }} of {{ total }}</span
    >
    <span class="dataset-progress__percent">{{
      progressCompletedPercent
    }}</span>
  </div>
</template>

<script>
export default {
  props: {
    total: {
      type: Number,
      required: true,
    },
    progressCompleted: {
      type: Number,
      required: true,
    },
    progressRanges: {
      type: Array,
      required: true,
    },
    loading: {
      type: Boolean,
      required: true,
    },
  },
  computed: {
    progressCompletedPercent() {
      return `${((this.progressCompleted / this.total) * 100).toFixed(2)}%`;
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-progress {
  position: relative;
  display: flex;
  align-items: center;
  gap: $base-space * 2;
  width: 100%;
  color: $black-54;
  @include font-size(12px);
  &__bar {
    width: 100%;
    max-width: 160px;
    box-shadow: 0 0 0 1px $black-10;
    border-radius: $border-radius-m;
  }
  &__data {
    font-weight: 500;
  }
  &__percent {
    font-weight: lighter;
  }
}
</style>
