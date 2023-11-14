<template>
  <span :class="['status-tag', getStatusInfo.class]">
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
      switch (this.recordStatus) {
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
        case "draft":
          return {
            name: "Pending",
            icon: null,
            class: "--pending",
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
  padding: 0.2em 1em;
  color: palette(white);
  @include font-size(13px);
  border-radius: 50px;
  font-weight: 600;

  &.--validated {
    background: palette(green);
    border: 1px solid palette(green);
  }

  &.--discarded {
    background: #a7a7a7;
    border: 1px solid #a7a7a7;
  }
  &.--submitted {
    background: $primary-color;
    border: 1px solid $primary-color;
  }
  &.--pending,
  &.--edited {
    background: palette(brown);
    border: 1px solid palette(brown);
  }

  .svg-icon {
    margin-right: 0.5em;
  }
}
</style>
