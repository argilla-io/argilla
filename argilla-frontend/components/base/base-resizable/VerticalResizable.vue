<template>
  <div class="resizable">
    <div class="resizable__left"><slot name="left" /></div>

    <div class="resizable__bar" ref="resizableBar">
      <div class="resizable__bar__inner" />
    </div>

    <div class="resizable__right"><slot name="right" /></div>
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
      element.style["max-width"] = "100%";
      element.style["min-width"] = "30%";
    },
    savePositionOnStartResizing(e) {
      this.leftSidePrevPosition = {
        clientX: e.clientX,
        width: this.leftSide.getBoundingClientRect().width,
      };
    },
    resize(e) {
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
    },
    mouseDownHandler(e) {
      this.savePositionOnStartResizing(e);

      document.addEventListener(EVENT.MOUSE_EVENT, this.mouseMoveHandler);
      document.addEventListener(EVENT.MOUSE_UP, this.mouseUpHandler);
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

.resizable {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  height: 100%;
  width: 100%;

  &__left {
    align-items: center;
    display: flex;
    justify-content: center;
  }

  &__right {
    flex: 1;
    align-items: center;
    display: flex;
    justify-content: center;
  }

  &__bar {
    height: 100%;
    width: $base-space;
    display: flex;
    justify-content: center;
    cursor: ew-resize;

    &__inner {
      height: 100%;
      border-left: thick solid lightgray;
      border-width: 1px;

      &:hover {
        border-width: 2px;
      }
    }

    &:hover {
      background-color: $card-primary-color;
    }
  }
}
</style>
