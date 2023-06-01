<template>
  <span>
    <div class="content__edition-area">
      <transition appear name="fade">
        <p
          ref="text"
          id="contentId"
          class="content__text"
          :class="textIsEdited ? '--edited-text' : null"
          :contenteditable="annotationEnabled"
          :placeholder="placeholder"
          @input="onInputText"
          v-html="editableText"
          @focus="setFocus(true)"
          @blur="setFocus(false)"
          @keydown.shift.backspace.exact="looseFocus"
          @keydown.shift.space.exact="looseFocus"
          @keydown.arrow-right.stop=""
          @keydown.arrow-left.stop=""
          @keydown.delete.exact.stop=""
          @keydown.enter.exact.stop=""
        />
      </transition>
      <span v-if="isShortcutToSave"><strong>shift Enter</strong> to save</span>
    </div>
  </span>
</template>
<script>
export default {
  props: {
    annotationEnabled: {
      type: Boolean,
      required: true,
    },
    annotations: {
      type: Array,
      required: true,
    },
    defaultText: {
      type: String,
      required: true,
    },
    placeholder: {
      type: String,
      default: "",
    },
    isShortcutToSave: {
      type: Boolean,
      default: () => true,
    },
  },
  data: () => {
    return {
      editableText: null,
      shiftPressed: false,
      shiftKey: undefined,
      focus: false,
    };
  },
  computed: {
    textIsEdited() {
      return (
        this.defaultText !== this.editableText ||
        this.defaultText === this.annotations[0]?.text
      );
    },
  },
  mounted() {
    window.addEventListener("keydown", this.keyDown);
    window.addEventListener("keyup", this.keyUp);
    window.addEventListener("paste", this.pastePlainText);

    if (this.defaultText) {
      this.editableText = this.defaultText;
    } else {
      this.editableText = this.text;
    }

    this.textAreaWrapper = document.getElementById("contentId");
  },
  destroyed() {
    window.removeEventListener("keydown", this.keyDown);
    window.removeEventListener("keyup", this.keyUp);
    window.removeEventListener("paste", this.pastePlainText);
  },
  methods: {
    looseFocus() {
      this.textAreaWrapper.blur();
    },
    onInputText(event) {
      this.$emit("change-text", event.target.innerText);
    },
    annotate() {
      if (this.defaultText && this.defaultText.trim()) {
        this.$emit("annotate");
      }
    },
    keyUp(event) {
      event.preventDefault();
      if (this.shiftKey === event.key) {
        this.shiftPressed = false;
      }
    },
    keyDown(event) {
      if (event.shiftKey) {
        this.shiftKey = event.key;
        this.shiftPressed = true;
      }
      const enter = event.key === "Enter";

      if (this.focus && this.shiftPressed && enter) {
        event.preventDefault();
        this.shiftPressed = false;
        this.annotate();
      }
    },
    setFocus(status) {
      this.focus = status;
      this.$emit("on-change-focus", status);
    },
    pastePlainText(event) {
      if (this.focus && event.target.isContentEditable) {
        event.preventDefault();
        const text = event.clipboardData.getData("text/plain");
        document.execCommand("insertText", false, text);
      }
    },
  },
};
</script>
<style lang="scss" scoped>
[contenteditable="true"] {
  padding: 0.6em;
  outline: none;
  &:focus + span {
    display: block;
  }
}
[contenteditable="true"]:empty:before {
  content: attr(placeholder);
  color: $black-37;
  pointer-events: none;
  display: block; /* For Firefox */
}
.content {
  &__edition-area {
    position: relative;
    width: 100%;
    span {
      position: absolute;
      top: 100%;
      right: 0;
      @include font-size(12px);
      color: palette(grey, verylight);
      margin-top: 0.5em;
      display: none;
    }
  }
  &__text {
    display: inline-block;
    width: 100%;
    min-height: 30px;
    height: 100%;
    color: $black-87;
    white-space: pre-wrap;
    margin: 0;
    word-break: break-word;
    font-style: italic;
    &.--edited-text {
      font-style: normal;
    }
  }
}
</style>
