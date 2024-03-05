<template>
  <span
    class="custom-cursor"
    :class="[cursorClass, { message: showHelperMessage }]"
    :data-title="showHelperMessage"
    ref="cursor"
    :style="{ left: cursorPosition.left, top: cursorPosition.top }"
  >
  </span>
</template>

<script>
export default {
  props: {
    cursorAreaRef: {
      type: String,
      required: true,
    },
    cursorColor: {
      type: String,
      default: "black",
    },
    showHelperMessage: {
      type: String,
      default: false,
    },
  },
  data() {
    return {
      cursorPosition: {
        left: 0,
        top: 0,
      },
      cursorClass: undefined,
    };
  },
  created() {
    this.area = this.$parent.$refs[this.cursorAreaRef];
  },
  methods: {
    addCursorClass() {
      this.cursorClass = "textual";
    },
    removeCursorClass() {
      this.cursorClass = "";
    },
    updateCursorPosition(e) {
      this.cursorPosition.left = e.clientX + "px";
      this.cursorPosition.top = e.clientY + "px";
    },
  },
  mounted() {
    if (!this.area) return;

    this.area.addEventListener("mouseover", this.addCursorClass);
    this.area.addEventListener("mouseleave", this.removeCursorClass);

    document.addEventListener("mousemove", this.updateCursorPosition);
  },
  destroyed() {
    if (!this.area) return;

    this.area.removeEventListener("mouseover", this.addCursorClass);
    this.area.removeEventListener("mouseleave", this.removeCursorClass);

    document.removeEventListener("mousemove", this.updateCursorPosition);
  },
};
</script>

<style lang="scss" scoped>
.custom-cursor {
  position: fixed;
  transform: translate(-50%, -50%);
  cursor: pointer;
}

.textual {
  cursor: none;
  pointer-events: none;
  height: 18px;
  width: 3px;
  background: v-bind(cursorColor);
  &.message {
    z-index: 200;
    &:after {
      position: absolute;
      height: auto;
      margin: 0;
      white-space: nowrap;
      content: attr(data-title);
      top: $base-space * 3;
      left: $base-space * 3;
      color: $black-87;
      padding: 0 calc($base-space / 2);
      border-radius: $border-radius;
      box-shadow: $shadow;
      background: palette(grey, 600);
      @include font-size(12px);
    }
  }
}
</style>
