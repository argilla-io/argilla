<template>
  <a
    class="sidebar-button"
    href="#"
    :data-title="tooltip"
    @click="$emit('button-action', id)"
  >
    <svgicon
      v-if="type !== 'Refresh'"
      v-show="activeView === id"
      class="sidebar-button__icon-help"
      :name="type === 'Mode' ? 'check3' : 'double-chev'"
    ></svgicon>
    <svgicon :name="icon"></svgicon>
  </a>
</template>

<script>
import "assets/icons/refresh";
import "assets/icons/explore-view";
import "assets/icons/annotate-view";
import "assets/icons/labelling-rules-view";
import "assets/icons/progress";
import "assets/icons/metrics";
import "assets/icons/double-chev";
import "assets/icons/check3";
export default {
  props: {
    activeView: {
      type: String,
      default: undefined,
    },
    tooltip: {
      type: String,
      required: true,
    },
    id: {
      type: String,
      required: true,
    },
    icon: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      required: true,
      validator: (value) => {
        return ["Mode", "Metrics", "Refresh"].includes(value);
      },
    },
  },
};
</script>

<style lang="scss" scoped>
$color: #333346;
.sidebar-button {
  &__icon-help {
    left: 5px;
    width: 11px !important;
    margin-right: 0;
    stroke-width: 2;
    position: absolute;
    left: 0.8em;
  }
}
.svg-icon {
  display: block;
  text-align: center;
  margin: auto;
  width: 24px;
  height: 24px;
  margin-bottom: 1.5em;
  fill: $color;
}
</style>
