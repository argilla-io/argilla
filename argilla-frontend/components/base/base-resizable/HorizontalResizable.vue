<template>
  <div class="resizable">
    <div class="resizable__up"><slot name="up" /></div>

    <div class="resizable__bar" ref="resizableBar">
      <span class="resizable__bar-button">:::</span>
    </div>

    <div class="resizable__down"><slot name="down" /></div>
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
      default: "h-rz",
    },
  },
  data() {
    return {
      upSidePrevPosition: {
        clientY: 0,
        height: 0,
      },
      resizer: null,
      upSide: null,
      downSide: null,
    };
  },
  mounted() {
    this.resizer = this.$refs.resizableBar;
    this.upSide = this.resizer.previousElementSibling;
    this.downSide = this.resizer.nextElementSibling;

    this.limitElementHeight(this.upSide);
    this.limitElementHeight(this.downSide);

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
      element.style["min-height"] = "15%";
    },
    savePositionOnStartResizing(e) {
      this.upSidePrevPosition = {
        clientY: e.clientY,
        height: this.upSide.getBoundingClientRect().height,
      };
    },
    resize(e) {
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
  flex-direction: column;
  gap: 15px;
  height: 100%;
  width: 100%;

  &__up {
    align-items: center;
    display: flex;
    justify-content: center;
  }

  &__down {
    flex: 1;
    align-items: center;
    display: flex;
    justify-content: center;
  }

  &__bar {
    border-bottom: thick solid lightgray;
    border-width: 1px;
    max-height: 5px;

    &-button {
      user-select: none;
      cursor: ns-resize;
      border-radius: $border-radius;
      align-items: center;
      background-color: $card-primary-color;
      color: white;
      padding: 3px;
      position: relative;
      left: 50%;
      top: -5px;

      &:hover {
        background: $card-secondary-color;
        box-shadow: $shadow-500;
      }
    }
  }
}
</style>
