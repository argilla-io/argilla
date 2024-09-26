<template>
  <div class="resizable" :class="resizing ? '--v-resizing' : ''">
    <div class="resizable__left"><slot name="left" /></div>

    <div class="resizable__bar" ref="resizableBar">
      <div class="resizable__bar__inner" />
    </div>

    <div class="resizable__right"><slot name="right" /></div>
    <slot></slot>
  </div>
</template>

<script>
import { useResizable } from "./useResizable";

const EVENT = {
  MOUSE_EVENT: "mousemove",
  MOUSE_UP: "mouseup",
  MOUSE_DOWN: "mousedown",
};

export default {
  props: {
    id: {
      type: String,
      default: "v-rz",
    },
  },
  data() {
    return {
      leftSidePrevPosition: {
        clientX: 0,
        width: 0,
      },
      resizer: null,
      leftSide: null,
      rightSide: null,
      resizing: false,
    };
  },
  mounted() {
    this.resizer = this.$refs.resizableBar;
    this.leftSide = this.resizer.previousElementSibling;
    this.rightSide = this.resizer.nextElementSibling;

    this.limitElementWidth(this.leftSide);
    this.limitElementWidth(this.rightSide);

    this.resizer.addEventListener(EVENT.MOUSE_DOWN, this.mouseDownHandler);

    const savedPosition = this.getPosition();
    if (savedPosition) {
      this.leftSide.style.width = savedPosition;
    }
  },
  destroyed() {
    this.resizer.removeEventListener(EVENT.MOUSE_DOWN, this.mouseDownHandler);
  },
  methods: {
    limitElementWidth(element) {
      element.style["max-width"] = "62%";
      element.style["min-width"] = "38%";
    },
    savePositionOnStartResizing(e) {
      this.leftSidePrevPosition = {
        clientX: e.clientX,
        width: this.leftSide.getBoundingClientRect().width,
      };
    },
    resize(e) {
      e.preventDefault();
      const dX = e.clientX - this.leftSidePrevPosition.clientX;
      const proportionalWidth = (this.leftSidePrevPosition.width + dX) * 100;
      const parentWidth = this.resizer.parentNode.getBoundingClientRect().width;

      const newLeftWidth = proportionalWidth / parentWidth;

      this.leftSide.style.width = `${newLeftWidth}%`;
    },

    mouseMoveHandler(e) {
      this.resize(e);
    },
    mouseUpHandler() {
      this.setPosition(`${this.leftSide.getBoundingClientRect().width}px`);

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
$resizabla-bar-color: #6794fe;
$resizable-bar-width: $base-space;

.resizable {
  $this: &;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  height: 100%;
  min-height: 0;
  width: 100%;
  &.--v-resizing {
    user-select: none;
  }

  &__left {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    width: 100%;
    margin-right: calc(-#{$resizable-bar-width} / 2);
    @include media("<desktop") {
      min-width: 100% !important;
      height: auto !important;
    }
  }

  &__right {
    display: flex;
    flex: 1;
    justify-content: center;
    align-items: center;
    height: 100%;
    margin-left: calc(-#{$resizable-bar-width} / 2);
    @include media("<desktop") {
      align-items: flex-end;
      min-width: 100% !important;
      height: auto !important;
      margin-left: 0;
    }
  }

  &__bar {
    height: 100%;
    width: $resizable-bar-width;
    display: flex;
    justify-content: center;
    z-index: 1;
    cursor: col-resize;
    @include media("<desktop") {
      display: none;
    }

    &__inner {
      height: 100%;
      border-left: 1px solid var(--bg-opacity-10);
      transition: all 0.1s ease-in;
    }

    &:hover,
    .--v-resizing & {
      #{$this}__bar__inner {
        transition: all 0.1s ease-in;
        border: 2px solid $resizabla-bar-color;
      }
    }
  }
}
</style>
