<template>
  <a
    class="sidebar-button"
    :class="sidebarButtonClass"
    href="#"
    :data-title="sidebarButtonTooltipText"
    @click="$emit('button-action', id)"
  >
    <svgicon :name="icon"></svgicon>
  </a>
</template>

<script>
import "assets/icons/refresh";
import "assets/icons/exploration";
import "assets/icons/hand-labeling";
import "assets/icons/weak-labeling";
import "assets/icons/progress";
import "assets/icons/stats";
export default {
  props: {
    activeView: {
      type: Array,
      default: () => [],
    },
    tooltip: {
      type: [String, null],
    },
    id: {
      type: String,
      required: true,
    },
    icon: {
      type: String,
      required: true,
    },
    buttonType: {
      type: [String, null],
      validator: (value) => {
        return ["Mode", "Metrics", "Refresh", "View-info", null].includes(value);
      },
    },
  },
  computed: {
    isActive() {
      return this.activeView.includes(this.id);
    },
    sidebarButtonClass() {
      return [
        this.buttonType?.toLowerCase(),
        this.isActive ? "active" : "",
      ];
    },
    sidebarButtonTooltipText() {
      return !this.isActive ? this.tooltip : null;
    },
  },
};
</script>

<style lang="scss" scoped>
.sidebar-button {
  &__icon-help {
    left: 5px;
    width: 11px !important;
    margin-right: 0;
    stroke-width: 2;
    position: absolute;
    left: 0.8em;
  }
  &.mode {
    &:hover {
      .svg-icon {
        background: palette(grey, 600);
        border-radius: $border-radius;
      }
    }
  }
  &.active {
    &.mode {
      .svg-icon {
        background: palette(grey, 600);
        border-radius: $border-radius;
      }
    }
    &.metrics {
      position: relative;
      .svg-icon {
        animation: move-horizontal 0.2s ease-in-out 0.2s;
        animation-fill-mode: backwards;
      }
      &.active:before {
        content: "";
        height: 38px;
        width: 2px;
        border-radius: 2px;
        position: absolute;
        left: 0;
        top: 0;
        background: palette(grey, 100);
      }
    }
  }
}
.svg-icon {
  display: block;
  text-align: center;
  margin: auto;
  width: 28px;
  height: 28px;
  fill: palette(grey, 100);
  padding: 0.5em;
  box-sizing: content-box;
  margin-bottom: 0.5em;
}

@keyframes move-horizontal {
  0% {
    transform: translateX(0.3em);
  }
  100% {
    transform: translateX(0);
  }
}
</style>
