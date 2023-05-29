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
    title: {
      type: String,
    },
  },
  computed: {
    getStatusInfo() {
      let statusInfo = null;
      switch (this.title.toUpperCase()) {
        case "PENDING":
          statusInfo = {
            name: "Pending",
            icon: null,
            class: "--pending",
          };
          break;
        case "EDITED":
          statusInfo = {
            name: "Pending",
            icon: "time",
            class: "--edited",
          };
          break;
        case "DISCARDED":
          statusInfo = {
            name: "Discarded",
            icon: "discard",
            class: "--discarded",
          };
          break;
        case "VALIDATED":
          statusInfo = {
            name: "Validate",
            icon: "validate",
            class: "--validated",
          };
          break;
        case "SUBMITTED":
          statusInfo = {
            name: "Submitted",
            icon: "validate",
            class: "--submitted",
          };
          break;
        default:
          console.log(`wrong status: ${this.title}`);
      }
      return statusInfo;
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
  &.--edited {
    background: #bb720a;
    border: 1px solid #bb720a;
  }
  &.--discarded {
    background: #a7a7a7;
    border: 1px solid #a7a7a7;
  }
  &.--submitted {
    background: $primary-color;
    border: 1px solid $primary-color;
  }
  &.--pending {
    background: #eeeeff;
    border: 1px solid #b6b9ff;
    color: #4c4ea3;
  }
  .svg-icon {
    margin-right: 0.5em;
  }
}
</style>
