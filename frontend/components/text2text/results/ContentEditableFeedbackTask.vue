<template>
  <span>
    <div
      class="content__edition-area"
      v-click-outside="{
        events: ['mousedown'],
        handler: onClickOutside,
      }"
    >
      <transition appear name="fade">
        <p
          ref="text"
          id="contentId"
          class="content__text"
          :class="textIsEdited ? '--edited-text' : null"
          :contenteditable="true"
          :placeholder="placeholder"
          @input="onInputText"
          v-html="sanitizedEditableText"
          @focus="setFocus(true)"
          @blur="setFocus(false)"
          @keydown.shift.enter.exact="looseFocus"
          @keydown.shift.backspace.exact="looseFocus"
          @keydown.shift.space.exact="looseFocus"
          @keydown.arrow-right.stop=""
          @keydown.arrow-left.stop=""
          @keydown.delete.exact.stop=""
          @keydown.enter.exact.stop=""
        />
      </transition>
    </div>
  </span>
</template>

<script>
import * as DOMPurify from "dompurify";
export default {
  name: "ContentEditableFeedbackTask",
  props: {
    value: {
      type: String,
      required: true,
    },
    placeholder: {
      type: String,
      default: "",
    },
  },
  data: () => {
    return {
      defaultText: null,
      currentValue: null,
      editableText: null,
      focus: false,
    };
  },
  computed: {
    textIsEdited() {
      return this.defaultText !== this.value;
    },
    sanitizedEditableText() {
      return DOMPurify.sanitize(this.editableText);
    },
  },
  watch: {
    value(newValue) {
      if (newValue !== this.currentValue) this.editableText = newValue;
    },
  },
  mounted() {
    window.addEventListener("paste", this.pastePlainText);

    this.editableText = this.defaultText = this.value;

    this.textAreaWrapper = document.getElementById("contentId");
  },
  destroyed() {
    window.removeEventListener("paste", this.pastePlainText);
  },
  methods: {
    looseFocus() {
      this.textAreaWrapper.blur();
    },
    onInputText(event) {
      this.currentValue = event.target.innerText;
      this.$emit("change-text", event.target.innerText);
    },
    setFocus(status) {
      this.focus = status;
      this.$emit("on-change-focus", status);
    },
    pastePlainText(event) {
      if (this.focus && event.target.isContentEditable) {
        event.preventDefault();
        const text = event.clipboardData?.getData("text/plain") ?? "";
        document.execCommand("insertText", false, text);
      }
    },
    onClickOutside() {
      this.setFocus(false);
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
