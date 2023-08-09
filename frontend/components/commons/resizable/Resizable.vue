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
  mounted() {
    const resizer = document.getElementById("resizableBar");

    const leftSide = resizer.previousElementSibling;
    const rightSide = resizer.nextElementSibling;

    this.limitElements(leftSide);
    this.limitElements(rightSide);

    let x = 0;
    let leftWidth = 0;

    const mouseMoveHandler = (e) => {
      const dx = e.clientX - x;

      const newLeftWidth =
        ((leftWidth + dx) * 100) /
        resizer.parentNode.getBoundingClientRect().width;

      leftSide.style.width = `${newLeftWidth}%`;
    };

    const mouseUpHandler = () => {
      document.removeEventListener("mousemove", mouseMoveHandler);
    };

    const mouseDownHandler = (e) => {
      x = e.clientX;
      leftWidth = leftSide.getBoundingClientRect().width;

      document.addEventListener("mousemove", mouseMoveHandler);
      document.addEventListener("mouseup", mouseUpHandler);
    };

    resizer.addEventListener("mousedown", mouseDownHandler);
  },
  methods: {
    limitElements(element) {
      const maxWith = this.$el.getBoundingClientRect().width;

      element.style["max-width"] = `${maxWith * 0.7}px`;
      element.style["min-width"] = `${maxWith * 0.3}px`;
    },
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
