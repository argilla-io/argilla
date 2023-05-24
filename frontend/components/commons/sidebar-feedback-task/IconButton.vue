<template>
  <BaseButton
    class="icon-button"
    :class="sidebarButtonClass"
    :data-title="tooltip"
    @on-click="onClickIcon"
  >
    <i
      :key="showBadge"
      class="icon-button__icon"
      v-badge="{
        showBadge: showBadge,
        verticalPosition: badgeVerticalPosition,
        horizontalPosition: badgeHorizontalPosition,
        borderColor: badgeBorderColor,
        size: badgeSize,
      }"
    >
      <svgicon :name="icon" :width="iconSize" :height="iconSize" />
    </i>
  </BaseButton>
</template>

<script>
export default {
  props: {
    id: {
      type: String,
      required: true,
    },
    icon: {
      type: String,
      required: true,
    },
    iconSize: {
      type: String,
      default: "28",
    },
    tooltip: {
      type: String,
    },
    showBadge: {
      type: Boolean,
      default: false,
    },
    badgeVerticalPosition: {
      type: String,
      default: "top",
    },
    badgeHorizontalPosition: {
      type: String,
      default: "right",
    },
    badgeSize: {
      type: String,
      default: "8px",
    },
    badgeBorderColor: {
      type: String,
    },
    buttonType: {
      type: String,
    },
    isButtonActive: {
      type: Boolean,
      default: false,
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
    onClickIcon() {
      this.$emit("on-button-action", this.id);
    },
  },
};
</script>

<style scoped lang="scss">
.icon-button {
  @include resetButtonStyles();
  width: 100%;
  display: flex;
  padding: 0;
  overflow: visible;
  border-radius: 0;
  &__icon {
    display: block;
    text-align: center;
    margin: auto;
    box-sizing: content-box;
    .svg-icon {
      padding: 0.5em;
      fill: palette(grey, 100);
    }
  }
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
      transition: none;
      .svg-icon {
        animation: move-horizontal 0.2s ease-in-out 0.2s;
        animation-fill-mode: backwards;
      }
      &.active {
        border-left: 2px solid palette(grey, 100);
      }
    }
  }
}

@keyframes move-horizontal {
  0% {
    transform: translateX(0.3em);
  }
  100% {
    transform: translateX(0);
  }
}
.icon-button[data-title] {
  position: relative;
  @extend %has-tooltip--left;
}
</style>
