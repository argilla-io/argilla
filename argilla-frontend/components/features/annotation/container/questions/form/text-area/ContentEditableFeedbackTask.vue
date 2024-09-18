<template>
  <span>
    <div
      class="content__edition-area"
      v-click-outside="{
        events: ['mousedown'],
        handler: onClickOutside,
      }"
    >
      <p
        ref="text"
        id="contentId"
        class="content__text"
        :class="classes"
        :contenteditable="true"
        :placeholder="placeholder"
        @input="onInputText"
        v-text="sanitizedCurrentValue"
        @focus="setFocus(true)"
        @blur="setFocus(false)"
        @keydown.stop=""
        @keydown.esc.exact="exitEditionMode"
        @paste="pastePlainText"
      />
    </div>
  </span>
</template>

<script>
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
    originalValue: {
      type: String,
      default: "",
    },
    isFocused: {
      type: Boolean,
      default: () => false,
    },
  },
  data: () => {
    return {
      sanitizedCurrentValue: null,
      currentValue: null,
    };
  },
  computed: {
    classes() {
      const classes = [];

      if (this.textIsEdited) {
        classes.push("--edited-text");
      }

      if (this.$language.isRTL(this.value)) {
        classes.push("--rtl");
      } else {
        classes.push("--ltr");
      }

      return classes;
    },
    textIsEdited() {
      return this.originalValue !== this.value;
    },
  },
  watch: {
    isFocused: {
      immediate: true,
      handler(newValue) {
        if (newValue) {
          this.$nextTick(() => {
            this.$refs.text.focus();
          });
        }
      },
    },
    value() {
      if (this.value !== this.currentValue) {
        this.reset();
      }
    },
  },
  mounted() {
    this.reset();
  },
  methods: {
    reset() {
      this.currentValue = this.value;
      this.sanitizedCurrentValue = " ";
      this.$nextTick(() => {
        this.sanitizedCurrentValue = this.currentValue;
      });
    },
    exitEditionMode() {
      this.$refs.text.blur();

      this.$emit("on-exit-edition-mode");
    },
    onInputText(event) {
      this.currentValue = event.target.innerText;
      this.$emit("change-text", this.currentValue);
    },
    setFocus(isFocus) {
      this.$emit("on-change-focus", isFocus);
    },
    pastePlainText(event) {
      if (event.target.isContentEditable) {
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
  color: var(--fg-tertiary);
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
      color: var(--bg-solid-grey-1);
      margin-top: 0.5em;
      display: none;
    }
  }
  &__text {
    display: inline-block;
    width: 100%;
    min-height: 30px;
    height: 100%;
    color: var(--fg-primary);
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
