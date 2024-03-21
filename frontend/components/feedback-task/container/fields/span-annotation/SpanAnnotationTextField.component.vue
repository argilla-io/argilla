<template>
  <div
    class="text_field_component"
    :key="name"
    @mouseenter.stop="mouseEnter = true"
    @mouseleave.stop="mouseEnter = false"
  >
    <div class="title-area --body2">
      <span class="text_field_component__title-content" v-text="title" />
      <BaseActionTooltip
        class="text_field_component__tooltip"
        tooltip="Copied"
        tooltip-position="left"
      >
        <BaseButton
          title="Copy to clipboard"
          class="text_field_component__copy-button"
          @click.prevent="$copyToClipboard(fieldText)"
        >
          <svgicon color="#acacac" name="copy" width="18" height="18" />
        </BaseButton>
      </BaseActionTooltip>
    </div>
    <div class="content-area --body1">
      <p
        class="span-annotation__field"
        :class="hasSelectedEntity ? 'span-annotation__field--active' : null"
        ref="spanAnnotationField"
        :id="id"
        v-html="fieldText"
        @mousedown="mouseDown = true"
        @mouseup="onMouseUp(false)"
        @mousemove="onMouseMove(mouseDown)"
      />
      <SpanAnnotationCursor
        v-if="hasSelectedEntity"
        cursor-area-ref="spanAnnotationField"
        :cursor-color="selectedEntityColor"
        :show-message="visibleShortcutsHelper"
        :show-entity="showCursorWithEntity"
        :entity-name="selectedEntity.text"
        :message="$t('spanAnnotation.shortcutHelper')"
      />
      <template v-for="{ id, color } in spanQuestion.answer.options">
        <style :key="id" scoped>
          .span-annotation__field::highlight(hl-{{id}}) {
            background-color: {{color}};
          }
        </style>
      </template>
    </div>
  </div>
</template>

<script>
import { useSpanAnnotationTextFieldViewModel } from "./useSpanAnnotationTextFieldViewModel";
export default {
  name: "SpanAnnotationTextFieldComponent",
  props: {
    id: {
      type: String,
      required: true,
    },
    name: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    fieldText: {
      type: String,
      required: true,
    },
    spanQuestion: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      visibleShortcutsHelper: false,
      alreadyUsedTheCharacterAnnotation: false,
      mouseDown: false,
      mouseTimeout: null,
      mouseEnter: false,
      showCursorWithEntity: false,
      timeOutShowEntity: null,
    };
  },
  computed: {
    selectedEntity() {
      return this.spanQuestion.answer.options.find((e) => e.isSelected);
    },
    selectedEntityColor() {
      return this.selectedEntity?.color;
    },
    hasSelectedEntity() {
      return !!this.selectedEntity;
    },
  },
  watch: {
    mouseEnter(newValue, oldValue) {
      if (newValue !== oldValue) {
        clearTimeout(this.timeOutShowEntity);
        this.showCursorWithEntity = true;
        this.timeOutShowEntity = setTimeout(() => {
          this.showCursorWithEntity = false;
        }, 3000);
      }
    },
  },
  methods: {
    allowCharacterAnnotation(allow) {
      this.highlighting.allowCharacterAnnotation(allow);
    },
    keyPressing(event, isDown) {
      if (event.key === "Shift") {
        window.getSelection()?.removeAllRanges();

        event.preventDefault();
        event.stopPropagation();

        this.allowCharacterAnnotation(isDown);
        this.alreadyUsedTheCharacterAnnotation = true;
        this.visibleShortcutsHelper = false;
      }
    },
    showShortcutsHelper(value) {
      if (!this.spanQuestion.settings.allow_character_annotation) return;
      if (this.alreadyUsedTheCharacterAnnotation) return;

      this.visibleShortcutsHelper = value;
    },
    onMouseUp(value) {
      this.mouseDown = value;
      if (this.mouseTimeout) clearTimeout(this.mouseTimeout);
      this.showShortcutsHelper(value);
    },
    onMouseMove(value) {
      this.mouseTimeout = setTimeout(() => {
        if (this.mouseDown) this.showShortcutsHelper(value);
      }, 500);
    },
    onKeyDown(event) {
      if (!this.spanQuestion.settings.allow_character_annotation) return;

      this.keyPressing(event, true);
    },
    onKeyUp(event) {
      if (!this.spanQuestion.settings.allow_character_annotation) return;

      this.keyPressing(event, false);
    },
  },
  mounted() {
    window.addEventListener("keydown", this.onKeyDown);
    window.addEventListener("keyup", this.onKeyUp);
  },
  destroyed() {
    window.removeEventListener("keydown", this.onKeyDown);
    window.removeEventListener("keyup", this.onKeyUp);
  },
  setup(props) {
    return useSpanAnnotationTextFieldViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.text_field_component {
  $this: &;
  user-select: text;
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: 2 * $base-space;
  background: palette(grey, 800);
  border-radius: $border-radius-m;
  &:hover {
    #{$this}__copy-button {
      opacity: 1;
    }
  }
  .title-area {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $base-space;
    color: $black-87;
  }
  .content-area {
    position: relative;
    white-space: pre-wrap;
    word-break: break-word;
  }
  &__title-content {
    word-break: break-word;
    width: calc(100% - 30px);
  }
  &__tooltip {
    display: flex;
    align-self: flex-start;
  }
  &__copy-button {
    flex-shrink: 0;
    padding: 0;
    opacity: 0;
  }
}

.span-annotation {
  &__field {
    position: relative;
    line-height: 32px;
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.span-annotation__field {
  margin: 0;
  &--active {
    cursor: none;
    &::selection {
      background-color: v-bind("selectedEntityColor");
    }
  }
}

:deep([id^="entity-span-container"]) {
  position: absolute;
  top: 0;
  left: 0;
}
</style>
