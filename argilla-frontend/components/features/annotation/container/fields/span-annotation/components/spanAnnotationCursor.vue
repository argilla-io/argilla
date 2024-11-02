<template>
  <span>
    <span
      v-if="showMessage"
      class="custom-cursor__message"
      :style="{ left: messagePosition.left, top: messagePosition.top }"
      v-text="message"
    />
    <span
      class="custom-cursor"
      :class="[cursorClass, { entity: showEntity }]"
      :data-message="message"
      :data-entity-name="entityName"
      ref="cursor"
      :style="{ left: cursorPosition.left, top: cursorPosition.top }"
    >
    </span>
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
    showMessage: {
      type: Boolean,
      default: false,
    },
    showEntity: {
      type: Boolean,
      default: false,
    },
    entityName: {
      type: String,
      required: true,
    },
    message: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      cursorPosition: {
        left: 0,
        top: 0,
      },
      messagePosition: {
        left: 0,
        top: 0,
      },
      cursorClass: undefined,
    };
  },
  created() {
    this.area = this.$parent.$refs[this.cursorAreaRef];
  },
  watch: {
    showMessage() {
      if (this.showMessage) this.messagePosition = { ...this.cursorPosition };
    },
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
  &__message {
    z-index: 1;
    position: fixed;
    transform: translate(-50%, calc(-50% - 30px));
    color: var(--color-white);
    padding: calc($base-space / 2);
    border-radius: $border-radius;
    box-shadow: $shadow-100;
    background: var(--color-dark-grey);
    @include font-size(12px);
    line-height: 1;
  }
}

.textual {
  cursor: none;
  pointer-events: none;
  height: 22px;
  width: 4px;
  background: v-bind(cursorColor);
  border: 1px solid var(--bg-accent-grey-2);
  [data-theme="dark"] & {
    background: v-bind("cursorColor.palette.veryDark");
  }
  &.entity {
    z-index: 200;
    &:before {
      position: absolute;
      height: auto;
      margin: 0;
      white-space: nowrap;
      content: attr(data-entity-name);
      bottom: $base-space * 2;
      transform: translate(-50%, -50%);
      left: 50%;
      padding: calc($base-space / 2);
      border-radius: $border-radius;
      box-shadow: $shadow-100;
      background: v-bind(cursorColor);
      @include font-size(10px);
      text-transform: uppercase;
      line-height: 1em;
      [data-theme="dark"] & {
        background: v-bind("cursorColor.palette.veryDark");
      }
    }
  }
}
</style>
