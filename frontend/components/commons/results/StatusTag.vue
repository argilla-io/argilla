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
      switch (this.title.toLowerCase()) {
        case "pending":
          return {
            name: "Pending",
            icon: null,
            class: "--pending",
          };
        case "edited":
          return {
            name: "Pending",
            icon: "time",
            class: "--edited",
          };
        case "discarded":
          return {
            name: "Discarded",
            icon: "discard",
            class: "--discarded",
          };
        case "validated":
          return {
            name: "Validate",
            icon: "validate",
            class: "--validated",
          };
        case "submitted":
          return {
            name: "Submitted",
            icon: "validate",
            class: "--submitted",
          };
        default:
          console.log(`wrong status: ${this.title}`);
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
  }
  &.--edited {
    background: #bb720a;
  }
  &.--discarded {
    background: #70767f;
  }
  &.--submitted {
    background: $primary-color;
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
