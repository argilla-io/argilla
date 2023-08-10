<template>
  <div class="resizable">
    <div class="resizable__left"><slot name="left" /></div>

    <div class="resizable__bar" ref="resizableBar">
      <span class="resizable__bar-button">:::</span>
    </div>

    <div class="resizable__right"><slot name="right" /></div>
  </div>
</template>

<script>
const EVENT = {
  MOUSE_EVENT: "mousemove",
  MOUSE_UP: "mouseup",
  MOUSE_DOWN: "mousedown",
};

export default {
  name: "Resizable",
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
  },
  methods: {
    limitElementWidth(element) {
      element.style["max-width"] = "70%";
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
      document.removeEventListener(EVENT.MOUSE_EVENT, this.mouseMoveHandler);
      document.removeEventListener(EVENT.MOUSE_UP, this.mouseUpHandler);
    },
    mouseDownHandler(e) {
      this.savePositionOnStartResizing(e);

      document.addEventListener(EVENT.MOUSE_EVENT, this.mouseMoveHandler);
      document.addEventListener(EVENT.MOUSE_UP, this.mouseUpHandler);
    },
  },
  destroyed() {
    this.resizer.removeEventListener(EVENT.MOUSE_DOWN, this.mouseDownHandler);
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
    border-left: thick solid lightgray;
    border-width: 1px;
    max-width: 5px;

    &-button {
      user-select: none;
      cursor: ew-resize;
      border-radius: $border-radius;
      align-items: center;
      background-color: $card-primary-color;
      border-radius: $border-radius;
      color: white;
      padding: 3px;
      position: relative;
      top: 50%;
      left: -9px;

      &:hover {
        background: $card-secondary-color;
        box-shadow: $shadow-500;
      }
    }
  }
}
</style>
