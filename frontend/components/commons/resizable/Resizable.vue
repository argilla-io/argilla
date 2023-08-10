<template>
  <div class="resizable">
    <div class="resizable__left"><slot name="left" /></div>

    <div class="resizable__bar" id="resizableBar">
      <span class="resizable__bar-button">:::</span>
    </div>

    <div class="resizable__right"><slot name="right" /></div>
  </div>
</template>

<script>
export default {
  name: "Resizable",
  data() {
    return {
      prevClientX: 0,
      prevLeftWith: 0,
      resizer: null,
      leftSide: null,
      rightSide: null,
    };
  },
  mounted() {
    this.resizer = document.getElementById("resizableBar");
    this.leftSide = this.resizer.previousElementSibling;
    this.rightSide = this.resizer.nextElementSibling;

    this.limitElements(this.leftSide);
    this.limitElements(this.rightSide);

    this.resizer.addEventListener("mousedown", this.mouseDownHandler);
  },
  methods: {
    limitElements(element) {
      const maxWith = this.$el.getBoundingClientRect().width;

      element.style["max-width"] = `${maxWith * 0.7}px`;
      element.style["min-width"] = `${maxWith * 0.3}px`;
    },
    mouseMoveHandler(e) {
      const dX = e.clientX - this.prevClientX;

      const newLeftWidth =
        ((this.prevLeftWith + dX) * 100) /
        this.resizer.parentNode.getBoundingClientRect().width;

      this.leftSide.style.width = `${newLeftWidth}%`;
    },
    mouseUpHandler() {
      document.removeEventListener("mousemove", this.mouseMoveHandler);
      document.removeEventListener("mouseup", this.mouseUpHandler);
    },
    mouseDownHandler(e) {
      this.prevClientX = e.clientX;
      this.prevLeftWith = this.leftSide.getBoundingClientRect().width;

      document.addEventListener("mousemove", this.mouseMoveHandler);
      document.addEventListener("mouseup", this.mouseUpHandler);
    },
  },
  destroyed() {
    this.resizer.removeEventListener("mousedown", this.mouseDownHandler);
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
