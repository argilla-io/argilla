<template>
  <span
    class="custom-cursor"
    :class="[
      cursorClass,
      { message: showMessage },
      { 'not-allowed': !allowAnnotation },
    ]"
    :data-title="showMessage"
    ref="cursor"
    :style="{ left: cursorPosition.left, top: cursorPosition.top }"
  >
    <svg viewBox="0 0 8 15" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M7.195 14.3707C7.195 14.7183 6.93012 15 6.6063 15H5.33909C4.7769 15 4.26895 14.7545 3.90102 14.358C3.53292 14.7545 3.02513 15 2.46278 15H1.19557C0.871757 15 0.606873 14.7183 0.606873 14.3707C0.606873 14.023 0.871757 13.7413 1.19557 13.7413H2.46278C2.93081 13.7413 3.312 13.3338 3.312 12.8335V2.16667C3.312 1.66633 2.93081 1.25883 2.46278 1.25883H1.19557C0.871757 1.25883 0.606873 0.977167 0.606873 0.6295C0.606717 0.281667 0.871757 0 1.19557 0H2.46278C3.02513 0 3.53292 0.2455 3.90086 0.642C4.2688 0.2455 4.77658 0 5.33894 0H6.60614C6.92996 0 7.19485 0.281667 7.19485 0.629333C7.19485 0.977 6.92996 1.25867 6.60614 1.25867H5.33894C4.87091 1.25867 4.48972 1.66617 4.48972 2.1665V12.8332C4.48972 13.3335 4.87091 13.741 5.33894 13.741H6.60614C6.92996 13.7412 7.195 14.0228 7.195 14.3707Z"
      />
    </svg>
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
    allowAnnotation: {
      type: Boolean,
      default: true,
    },
    showMessage: {
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
  svg {
    display: block;
    width: 10px;
    fill: black;
    stroke: v-bind(cursorColor);
    filter: drop-shadow(0 0 1px white);
  }
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
      background: palette(white);
      @include font-size(12px);
    }
  }
  &.not-allowed {
    height: 0;
    width: 0;
    &:after {
      top: 0;
      left: 0;
      @include font-size(13px);
      background: v-bind(cursorColor);
    }
  }
}
</style>
