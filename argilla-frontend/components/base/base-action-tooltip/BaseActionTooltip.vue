<template>
  <span
    :class="['tooltip__container', showTooltip ? 'active' : null]"
    @click="active()"
  >
    <slot></slot>
    <span
      v-if="tooltip && showTooltip"
      class="tooltip"
      :class="tooltipClass"
      v-text="tooltip"
    />
  </span>
</template>

<script>
export default {
  data: () => {
    return {
      showTooltip: false,
    };
  },
  props: {
    tooltip: {
      type: String,
    },
    tooltipPosition: {
      type: String,
      default: "right",
    },
  },
  computed: {
    tooltipClass() {
      return `--${this.tooltipPosition}`;
    },
  },
  methods: {
    active() {
      this.showTooltip = true;
      setTimeout(() => {
        this.showTooltip = undefined;
      }, 1000);
    },
  },
};
</script>

<style scoped lang="scss">
.tooltip {
  position: absolute;
  top: 0;
  background: var(--bg-tooltip);
  display: inline-block;
  border-radius: $border-radius-s;
  color: var(--color-white);
  @include font-size(12px);
  box-shadow: 0 1px 4px 1px var(--bg-accent-grey-1);
  padding: 0.1em 0.5em;
  white-space: nowrap;
  font-family: $primary-font-family !important;
  z-index: 1;
  &.--left {
    right: 100%;
  }
  &.--right {
    left: 100%;
  }
  &__container {
    position: relative;
  }
}
</style>
