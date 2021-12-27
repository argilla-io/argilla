<template>
  <span>
    <div class="content__edition-area">
      <p
        ref="text"
        class="content__text"
        :contenteditable="contentEditable"
        :placeholder="placeholder"
        @input="onInputText"
        @click="$emit('edit')"
        v-html="editableText"
      ></p>
      <span v-if="editionMode"><strong>shift Enter</strong> to save</span>
    </div>
    <div
      v-if="editionMode && annotationEnabled && editableText"
      class="content__edit__buttons"
    >
      <re-button class="button-primary--outline" @click="$emit('back')"
        >Back</re-button
      >
      <re-button class="button-primary" @click="annotate">Save</re-button>
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
    editionMode: {
      type: Boolean,
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
  },
  data: () => {
    return {
      editableText: undefined,
      shiftPressed: false,
      shiftKey: undefined,
    };
  },
  computed: {
    contentEditable() {
      return this.annotationEnabled && this.editionMode;
    },
  },
  mounted() {
    window.addEventListener("keydown", this.keyDown);
    window.addEventListener("keyup", this.keyUp);
    if (this.defaultText) {
      this.editableText = this.defaultText;
    } else {
      this.editableText = this.text;
    }
  },
  destroyed() {
    window.removeEventListener("keydown", this.keyDown);
    window.addEventListener("keyup", this.keyUp);
  },
  methods: {
    onInputText(event) {
      this.$emit("change-text", event.target.innerText);
    },
    annotate() {
      if (this.defaultText && this.defaultText.trim()) {
        this.$emit("annotate", this.defaultText);
      }
    },
    keyUp(event) {
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
      if (this.shiftPressed && this.editionMode && enter) {
        this.annotate();
      }
    },
  },
};
</script>
<style lang="scss" scoped>
$marginRight: 200px;
[contenteditable="true"] {
  box-shadow: 0 1px 4px 1px rgba(222, 222, 222, 0.5);
  border-radius: 3px 3px 3px 3px;
  &:focus + span {
    display: block;
  }
}
[contenteditable="true"]:empty:before {
  color: palette(grey, verylight);
  content: attr(placeholder);
  pointer-events: none;
  display: block; /* For Firefox */
}
.content {
  &__edition-area {
    position: relative;
    margin-right: $marginRight;
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
    color: black;
    white-space: pre-wrap;
    display: inline-block;
    width: 100%;
  }
  &__edit {
    &__buttons {
      margin: 2.5em 200px 0 auto;
      display: flex;
      justify-content: flex-end;
      .re-button {
        margin-bottom: 0;
        &:last-child {
          transition: margin 0s ease;
          margin-left: 6px;
        }
      }
    }
  }
}
</style>
