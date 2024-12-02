<template>
  <div
    class="text_field_component"
    :key="id"
    @mouseenter.stop="mouseEnter = true"
    @mouseleave.stop="mouseEnter = false"
    aria-label="Data Record Field"
  >
    <div class="title-area --body2">
      <span
        class="text_field_component__title-content"
        v-text="title"
        :aria-label="'Field Name: ' + title"
      />
      <BaseActionTooltip
        class="text_field_component__tooltip"
        :tooltip="$t('copied')"
        tooltip-position="left"
      >
        <BaseButton
          :title="$t('button.tooltip.copyToClipboard')"
          :aria-label="$t('button.tooltip.copyToClipboard')"
          class="text_field_component__copy-button"
          @click.prevent="$copyToClipboard(fieldText)"
          role="button"
        >
          <svgicon
            color="#acacac"
            name="copy"
            width="18"
            height="18"
            aria-hidden="true"
          />
        </BaseButton>
      </BaseActionTooltip>
    </div>
    <div
      :id="`fields-content-${id}`"
      class="text_field_component__area --body1"
      :aria-label="'Data entry for Field: ' + title"
    >
      <p
        :class="[
          allowOverlapping
            ? 'span-annotation__field--overlapped'
            : 'span-annotation__field',
          hasSelectedEntity ? 'span-annotation__field--active' : null,
        ]"
        ref="spanAnnotationField"
        :id="id"
        v-html="fieldText"
        tabindex="0"
        @mousedown="onMouseDown"
        @mouseup="onMouseUp"
        @mousemove="onMouseMove"
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
      <template>
        <template v-for="{ id, color } in spanQuestion.answer.options">
          <style :key="id" scoped>
            .span-annotation__field::highlight(hl-{{id}}), .span-annotation__field::highlight(hl-{{id}}-selection) {
              background-color: {{color}};
            }
            [data-theme="dark"] .span-annotation__field::highlight(hl-{{id}}), [data-theme="dark"] .span-annotation__field::highlight(hl-{{id}}-selection) {
              background-color: {{color.palette.veryDark}};
            }
            .span-annotation__field::highlight(hl-{{id}}-pre-selection) {
              background: {{color.palette.light}};
            }
            [data-theme="dark"] .span-annotation__field::highlight(hl-{{id}}-pre-selection) {
              background: {{color.palette.dark}};
            }
            .span-annotation__field--overlapped::highlight(hl-{{id}}-selection) {
              background: {{color}};
            }
            [data-theme="dark"] .span-annotation__field--overlapped::highlight(hl-{{id}}-selection) {
              background: {{color.palette.veryDark}};
            }
            .span-annotation__field--overlapped::highlight(hl-{{id}}-pre-selection) {
              background: {{color.palette.light}};
              color: inherit;
            }
            [data-theme="dark"] .span-annotation__field--overlapped::highlight(hl-{{id}}-pre-selection) {
              background: {{color.palette.dark}};
            }
            .span-annotation__field--overlapped::highlight(hl-{{id}}-hover) {
              background: {{color}};
            }
            [data-theme="dark"] .span-annotation__field--overlapped::highlight(hl-{{id}}-hover) {
              background: {{color.palette.veryDark}};
            }
            ::highlight(search-text-highlight-{{id}}) {
              color: #ff675f;
            }
          </style>
        </template>
      </template>
    </div>
  </div>
</template>

<script>
import { useSpanAnnotationTextFieldViewModel } from "./useSpanAnnotationTextFieldViewModel";
export default {
  props: {
    id: {
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
    searchText: {
      type: String,
      default: "",
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
    lineHeight() {
      return `${this.highlighting.config.lineHeight}px`;
    },
    selectedEntity() {
      return this.spanQuestion.answer.options.find((e) => e.isSelected);
    },
    selectedEntityColor() {
      return this.selectedEntity?.color;
    },
    hasSelectedEntity() {
      return !!this.selectedEntity;
    },
    allowOverlapping() {
      return this.highlighting.config.allowOverlap;
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
    onMouseDown() {
      this.mouseDown = true;
    },
    onMouseUp() {
      this.mouseDown = false;
      if (this.mouseTimeout) clearTimeout(this.mouseTimeout);

      this.showShortcutsHelper(false);
    },
    onMouseMove() {
      const mouseDown = this.mouseDown;
      this.mouseTimeout = setTimeout(() => {
        if (this.mouseDown) this.showShortcutsHelper(mouseDown);
      }, 500);
    },
    onKeyDown(event) {
      this.keyPressing(event, true);
    },
    onKeyUp(event) {
      this.keyPressing(event, false);
    },
  },
  mounted() {
    if (!this.spanQuestion.settings.allow_character_annotation) return;

    document.addEventListener("keydown", this.onKeyDown);
    document.addEventListener("keyup", this.onKeyUp);
  },
  beforeDestroy() {
    if (!this.spanQuestion.settings.allow_character_annotation) return;

    document.removeEventListener("keydown", this.onKeyDown);
    document.removeEventListener("keyup", this.onKeyUp);
  },
  setup(props) {
    return useSpanAnnotationTextFieldViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.text_field_component {
  $this: &;
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: 2 * $base-space;
  background: var(--bg-field);
  border-radius: $border-radius-m;
  border: 1px solid var(--border-field);
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
    color: var(--fg-primary);
  }
  &__area {
    position: relative;
    white-space: pre-wrap;
    word-break: break-word;
    user-select: none;
  }
  &__title-content {
    word-break: break-word;
    width: calc(100% - 30px);
    color: var(--fg-secondary);
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
    margin: 0;
    @include font-size(16px);
    line-height: v-bind(lineHeight);
    user-select: text;
    &--overlapped {
      @extend .span-annotation__field;
    }
    &--active {
      cursor: none;
      &::selection {
        background-color: transparent;
      }
    }
    &:focus {
      outline: none;
    }
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

:deep([id^="entity-span-container"]) {
  position: absolute;
  top: 0;
  left: 0;
}
::highlight(search-text-highlight) {
  color: var(--fg-highlight);
}
</style>
