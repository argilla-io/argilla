<template>
  <div class="resizable" :class="resizing ? '--resizing' : null">
    <div class="resizable__up">
      <slot name="up" />
    </div>

    <div v-if="isDownExpanded" class="resizable__bar" ref="resizableBar">
      <div class="resizable__bar__inner" />
    </div>
    <div v-else class="resizable__bar__inner--no-hover" ref="resizableBar" />
    <div
      class="resizable__down"
      :class="isDownExpanded ? '--expanded' : null"
      :key="isDownExpanded"
    >
      <BaseButton
        class="resizable__header"
        @click="isDownExpanded = !isDownExpanded"
      >
        <slot name="downHeader" />
        <svgicon
          class="resizable__header__icon"
          :name="isDownExpanded ? 'chevron-down' : 'chevron-right'"
          width="12"
          height="12"
        />
      </BaseButton>

      <div class="resizable__content" v-show="isDownExpanded">
        <slot name="downContent" />
      </div>
    </div>
  </div>
</template>

<script>
import "assets/icons/chevron-right";
import "assets/icons/chevron-down";
import { useResizable } from "./useResizable";
import BaseButton from "../base-button/BaseButton.vue";

const EVENT = {
  MOUSE_EVENT: "mousemove",
  MOUSE_UP: "mouseup",
  MOUSE_DOWN: "mousedown",
};

export default {
  components: { BaseButton },
  props: {
    id: {
      type: String,
      default: "h-rz",
    },
  },
  data() {
    return {
      resizing: false,
      isDownExpanded: false,
      upSidePrevPosition: {
        clientY: 0,
        height: 0,
      },
      resizer: null,
      upSide: null,
      downSide: null,
    };
  },
  watch: {
    isDownExpanded() {
      if (this.isDownExpanded) {
        this.upSide.style.height = "60%";
      } else {
        this.upSide.style.height = "100%";
      }

      this.$nextTick(() => {
        this.setPosition(`${this.upSide.getBoundingClientRect().height}px`);
      });
    },
  },
  mounted() {
    this.resizer = this.$refs.resizableBar;
    this.upSide = this.resizer.previousElementSibling;
    this.downSide = this.resizer.nextElementSibling;

    this.limitElementHeight(this.upSide);

    this.resizer.addEventListener(EVENT.MOUSE_DOWN, this.mouseDownHandler);

    const savedPosition = this.getPosition();
    if (savedPosition) {
      this.upSide.style.height = savedPosition;
    }
  },
  destroyed() {
    this.resizer.removeEventListener(EVENT.MOUSE_DOWN, this.mouseDownHandler);
  },
  methods: {
    limitElementHeight(element) {
      element.style["max-height"] = "100%";
      element.style["min-height"] = "50%";
    },
    savePositionOnStartResizing(e) {
      this.upSidePrevPosition = {
        clientY: e.clientY,
        height: this.upSide.getBoundingClientRect().height,
      };
    },
    resize(e) {
      e.preventDefault();
      const dY = e.clientY - this.upSidePrevPosition.clientY;
      const proportionalHeight = (this.upSidePrevPosition.height + dY) * 100;
      const parentHeight =
        this.resizer.parentNode.getBoundingClientRect().height;

      const newHeight = proportionalHeight / parentHeight;

      this.upSide.style.height = `${newHeight}%`;
    },
    mouseMoveHandler(e) {
      this.resize(e);
    },
    mouseUpHandler() {
      this.setPosition(`${this.upSide.getBoundingClientRect().height}px`);

      document.removeEventListener(EVENT.MOUSE_EVENT, this.mouseMoveHandler);
      document.removeEventListener(EVENT.MOUSE_UP, this.mouseUpHandler);
      this.resizing = false;
    },
    mouseDownHandler(e) {
      this.savePositionOnStartResizing(e);

      document.addEventListener(EVENT.MOUSE_EVENT, this.mouseMoveHandler);
      document.addEventListener(EVENT.MOUSE_UP, this.mouseUpHandler);
      this.resizing = true;
    },
  },
  setup(props) {
    return useResizable(props);
  },
};
</script>
<style lang="scss" scoped>
$card-primary-color: #e0e0ff;
$card-secondary-color: palette(purple, 200);
$card-height: 50px;
.resizable {
  display: flex;
  justify-content: space-between;
  flex-direction: column;
  height: 100%;
  width: 100%;
  &.--resizing {
    user-select: none;
  }

  &__header {
    width: 100%;
    height: $card-height;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $base-space $base-space * 2;
    @include font-size(13px);
    :deep(p) {
      text-transform: uppercase;
    }
    &__icon {
      padding: 0;
      flex-shrink: 0;
    }
  }

  &__content {
    width: 100%;
    height: 100%;
    padding: $base-space $base-space * 2;
    overflow: scroll;
    @include font-size(13px);
  }

  &__up {
    align-items: center;
    display: flex;
    justify-content: center;
    min-height: $card-height;
    transition: all 0.2s ease-in;
    @include media("<desktop") {
      height: auto !important;
    }
    .--resizing & {
      transition: none;
    }
  }

  &__down {
    flex: 1;
    align-items: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: $card-height;
  }

  &__bar {
    height: $base-space;
    width: 100%;
    display: flex;
    align-items: center;
    z-index: 1;
    cursor: ns-resize;
    @include media("<desktop") {
      display: none;
    }

    &__inner {
      width: 100%;
      border-bottom: thick solid $black-10;
      border-width: 1px;

      &:hover {
        border-width: 2px;
      }
    }

    &__inner--no-hover {
      width: 100%;
      border-bottom: thick solid $black-10;
      border-width: 1px;
    }

    &:hover {
      background-color: $card-primary-color;
    }
  }
}

.transition-enter-active,
.transition-leave-active {
  transition: all 2s ease-in-out;
}
.transition-enter-from,
.transition-leave-to {
  min-height: 0;
}
</style>
