<template>
  <span
    :key="record.status"
    :class="['status-tag', getStatusInfo.class]"
    :title="getStatusInfo.name"
    ><span class="bullet"></span>

    <span>{{ getStatusInfo.name }}</span>
    <span
      v-if="record.isDraft && record.taskDistribution.isCompleted"
      class="circle"
      :data-title="$t('recordStatus.completedTooltip')"
    >
      <svgicon class="check" name="check" width="12" height="12"></svgicon>
    </span>
  </span>
</template>

<script>
export default {
  props: {
    record: {
      type: Object,
      required: true,
    },
  },
  computed: {
    getStatusInfo() {
      switch (this.record.status) {
        case "pending":
          return {
            name: this.$tc("recordStatus.pending", 1),
            class: "--pending",
          };
        case "draft":
          return {
            name: this.$tc("recordStatus.draft", 1),
            class: "--draft",
          };

        case "discarded":
          return {
            name: this.$tc("recordStatus.discarded", 1),
            class: "--discarded",
          };

        case "submitted":
          return {
            name: this.$tc("recordStatus.submitted", 1),
            class: "--submitted",
          };
      }
    },
  },
};
</script>

<style scoped lang="scss">
%bullet {
  content: "";
  display: inline-block;
  width: $base-space;
  height: $base-space;
  border-radius: $border-radius-rounded;
}
.status-tag {
  text-transform: capitalize;
  display: flex;
  align-items: center;
  gap: $base-space;
  @include font-size(13px);
  font-weight: 500;

  &.--discarded {
    color: $discarded-color;
    .bullet:before {
      @extend %bullet;
      background: $discarded-color;
    }
  }
  &.--submitted {
    color: $submitted-color;
    .bullet:before {
      @extend %bullet;
      background: $submitted-color;
    }
  }
  &.--pending {
    color: $pending-color;
    .bullet:before {
      @extend %bullet;
      background: $pending-color;
    }
  }
  &.--draft {
    color: $draft-color;
    .bullet:before {
      @extend %bullet;
      background: $draft-color;
    }
    .check {
      color: $draft-color;
      flex-shrink: 0;
    }
    .circle {
      border: 2px solid $draft-color;
    }
  }
}
.circle {
  z-index: 99;
  display: flex;
  align-items: center;
  border-radius: 50%;
}
[data-title] {
  position: relative;
  overflow: visible;
  @include tooltip-mini("top", 8px);
}
</style>
