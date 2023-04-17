<template>
  <button
    class="sidebar-button"
    :class="sidebarButtonClass"
    :data-title="tooltip"
    @click="onButtonClick"
  >
    <svgicon :name="icon"></svgicon>
  </button>
</template>

<script>
export default {
  props: {
    isButtonActive: {
      type: Boolean,
      default: false,
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
      required: true,
    },
  },
  computed: {
    sidebarButtonClass() {
      return [this.buttonTypeClass, this.buttonStateClass];
    },
    buttonTypeClass() {
      return this.buttonType;
    },
    buttonStateClass() {
      return this.isButtonActive ? "active" : null;
    },
  },
  methods: {
    onButtonClick() {
      this.$emit("on-button-action", this.id);
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
  &.non-expandable {
    &:hover {
      .svg-icon {
        background: palette(grey, 600);
        border-radius: $border-radius;
      }
    }
  }
  &.active {
    &.non-expandable {
      .svg-icon {
        background: palette(grey, 600);
        border-radius: $border-radius;
      }
    }
    &.expandable {
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
button[data-title] {
  position: relative;
  @extend %has-tooltip--left;
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
