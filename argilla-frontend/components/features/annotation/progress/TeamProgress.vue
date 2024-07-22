<template>
  <div class="team-progress">
    <BaseLinearProgress
      class="team-progress__bar"
      :progress-ranges="progressRanges"
      :progress-max="progress.total"
    />
    <span class="team-progress__percent"
      >{{ progress.percentage.completed }}%</span
    >
    <span v-if="visibleProgressValues" class="team-progress__info">
      {{ progress.completed }} of {{ progress.total }}
    </span>
  </div>
</template>

<script>
import { useTeamProgressViewModel } from "./useTeamProgressViewModel";

export default {
  props: {
    datasetId: {
      type: String,
      required: true,
    },
    visibleProgressValues: {
      type: Boolean,
    },
  },
  computed: {
    progressRanges() {
      return [
        {
          id: "completed",
          name: "completed",
          color: "linear-gradient(90deg, #6A6A6C 0%, #252626 100%)",
          value: this.progress.completed,
        },
        {
          id: "pending",
          name: "progress",
          color: "linear-gradient(white)",
          value: this.progress.pending,
        },
      ];
    },
  },
  setup(props) {
    return useTeamProgressViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.team-progress {
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
  }
  &__data {
    font-weight: 500;
  }
  &__percent {
    font-weight: lighter;
  }
}
</style>
