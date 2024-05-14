<template>
  <button
    class="sidebar-button"
    :class="sidebarButtonClass"
    :data-title="tooltip"
    @click="$emit('button-action', id)"
  >
    <svgicon :name="icon"></svgicon>
  </button>
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
      type: String,
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
      type: String,
      validator: (value) => {
        return ["Mode", "Metrics", "Refresh"].includes(value);
      },
    },
  },
  computed: {
    isActive() {
      return this.activeView.includes(this.id);
    },
    sidebarButtonClass() {
      return [this.buttonTypeClass, this.buttonStateClass];
    },
    buttonTypeClass() {
      return this.buttonType?.toLowerCase();
    },
    buttonStateClass() {
      return this.isActive ? "active" : null;
    },
  },
};
</script>

<style lang="scss" scoped>
.sidebar-button {
  @include resetButtonStyles();
  width: 100%;
  display: flex;
  margin-bottom: 0.5em;
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
      &.active {
        border-left: 2px solid palette(grey, 100);
      }
    }
  }
  &:hover {
    cursor: pointer;
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
