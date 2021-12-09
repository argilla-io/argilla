<template>
  <span>
    <div class="content__edition-area">
      <p
        ref="text"
        class="content__text"
        :contenteditable="contentEditable"
        :placeholder="placeholder"
        @input="$emit('text', $event)"
        v-html="editableText"
        @click="$emit('edit')"
      ></p>
      <span v-if="editionMode"
        ><strong>shift Enter</strong> to save</span
      >
    </div>
    <div class="content__edit__buttons" v-if="editionMode && annotationEnabled && editableText">
      <re-button
        class="button-primary--outline"
        @click="$emit('back')"
        >Back</re-button
      >
      <re-button
        class="button-primary"
        @click="annotate()"
        >Save</re-button
      >
    </div>
  </span>
</template>
<script>
export default {
  props: {
    contentEditable: {
      type: Boolean,
      required: true,
    },
    annotationEnabled: {
      type: Boolean,
      required: true,
    },
    editionMode: {
      type: Boolean,
      required: true,
    },
    text: {
      type: String,
      required: true,
    },
    newSentence: {
      type: String,
      default: undefined,      
    },
    placeholder: {
      type: String,    
    },
  },
  data: () => {
    return {
      editableText: undefined,
      shiftPressed: false,
      shiftKey: undefined,
    }
  },
  mounted() {
      if (this.newSentence) {
        this.editableText = this.newSentence;
      } else {
        this.editableText = this.text;
      }
  },
  created() {
    window.addEventListener("keydown", this.keyDown);
    window.addEventListener("keyup", this.keyUp);
  },
  destroyed() {
    window.removeEventListener("keydown", this.keyDown);
    window.addEventListener("keyup", this.keyUp);
  },
  methods: {
    annotate() {
      this.$emit('annotate', this.editableText);
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
  }
}
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


