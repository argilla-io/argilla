<template>
  <span
    :key="recordStatus"
    :class="['status-tag', getStatusInfo.class]"
    :title="getStatusInfo.name"
  >
    <svgicon
      v-if="getStatusInfo.icon"
      :name="getStatusInfo.icon"
      width="14"
      height="14"
      color="#ffffff"
    ></svgicon>
    {{ getStatusInfo.name }}
  </span>
</template>

<script>
import "assets/icons/validate";
import "assets/icons/time";
import "assets/icons/discard";
export default {
  props: {
    recordStatus: {
      type: String,
    },
  },
  computed: {
    getStatusInfo() {
      switch (this.recordStatus.toLowerCase()) {
        case "validated":
          return {
            name: "Validate",
            icon: "validate",
            class: "--validated",
          };

        case "edited":
          return {
            name: "Pending",
            icon: "time",
            class: "--edited",
          };

        case "pending":
          return {
            name: "Pending",
            icon: null,
            class: "--pending",
          };
        case "draft":
          return {
            name: "Draft",
            icon: null,
            class: "--draft",
          };

        case "discarded":
          return {
            name: "Discarded",
            icon: "discard",
            class: "--discarded",
          };

        case "submitted":
          return {
            name: "Submitted",
            icon: "validate",
            class: "--submitted",
          };
      }
    },
  },
};
</script>

<style scoped lang="scss">
.status-tag {
  display: inline-flex;
  z-index: 0;
  align-items: center;
  padding: 0.1em $base-space;
  color: palette(white);
  @include font-size(13px);
  border-radius: 50px;
  font-weight: 500;

  &.--validated {
    background: palette(green);
    border: 1px solid palette(green);
  }

  &.--discarded {
    background: $discarded-color;
    border: 1px solid $discarded-color;
  }
  &.--submitted {
    background: $submitted-color;
    border: 1px solid $submitted-color;
  }
  &.--pending,
  &.--edited {
    background: $pending-color;
    border: 1px solid $pending-color;
  }
  &.--draft {
    background: $draft-color;
    border: 1px solid $draft-color;
  }

  .svg-icon {
    margin-right: 0.5em;
  }
}
</style>
