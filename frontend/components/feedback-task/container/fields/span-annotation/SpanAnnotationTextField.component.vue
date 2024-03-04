<template>
  <div class="text_field_component" :key="fieldText">
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
        ref="spanAnnotationField"
        :id="title"
        v-html="fieldText"
      />
      <SpanAnnotationCursor
        cursor-area-ref="spanAnnotationField"
        :cursor-color="selectedEntityColor"
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
    },
  },
  computed: {
    selectedEntity() {
      return this.spanQuestion.answer.options.find((e) => e.isSelected);
    },
    selectedEntityColor() {
      return this.selectedEntity?.color;
    },
  },
  methods: {
    allowCharacterAnnotation(allow) {
      this.highlighting.allowCharacterAnnotation(allow);
    },
    keyPressing(event, isDown) {
      if (event.key == "Shift") {
        this.allowCharacterAnnotation(isDown);
      }
    },
  },
  mounted() {
    window.addEventListener("keydown", (event) =>
      this.keyPressing(event, true)
    );
    window.addEventListener("keyup", (event) => this.keyPressing(event, false));
  },
  destroyed() {
    window.removeEventListener("keydown", (event) =>
      this.keyPressing(event, true)
    );
    window.removeEventListener("keyup", (event) =>
      this.keyPressing(event, false)
    );
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
    cursor: none;
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

::selection {
  background-color: v-bind("selectedEntityColor");
}

:deep(#entity-span-container) {
  position: absolute;
  top: 0;
  left: 0;
}
</style>
