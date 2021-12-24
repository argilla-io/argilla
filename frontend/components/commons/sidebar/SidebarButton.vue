<template>
  <a class="sidebar-button"
    href="#"
    :data-title="tooltip"
    @click="$emit('change-view-mode', id)"
  >
    <svgicon
      v-show="activeView === id"
      class="sidebar-button__icon-help"
      name="check3"
    ></svgicon>
    <svgicon :name="icon"></svgicon>
  </a>
</template>

<script>
export default {
  props: {
    activeView: {
      type: String,
    },
    tooltip: {
      type: String,
    },
    id: {
      type: String,
    },
    icon: {
      type: String,
    }
  }
}
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

