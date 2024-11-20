<template>
  <div class="dataset-progress">
    <p class="dataset-progress__title">{{ $t("metrics.progress.team") }}</p>
    <p class="dataset-progress__percent">{{ getPercent }}%</p>
  </div>
</template>

<script>
export default {
  props: {
    percent: {
      type: String,
      required: true,
    },
  },
  computed: {
    getPercent() {
      return isNaN(this.percent) ? "-" : this.percent;
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-progress {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: $base-space;
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
