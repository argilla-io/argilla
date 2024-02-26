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
      <p class="span-annotation__field" :id="title" v-html="fieldText" />
      <template v-for="{ id, color } in spanQuestion.answer.entities">
        <style :key="id" scoped>
          ::highlight(hl-{{id}}) {
            background-color: {{color}};
            text-decoration: {{color}} solid underline 10px;
            text-underline-offset: 4px;
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
      return this.spanQuestion.answer.entities.find((e) => e.isSelected);
    },
    selectedEntityColor() {
      return this.selectedEntity?.color;
    },
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
    line-height: 1.9em;
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
</style>

<style>
.highlight__entity {
  display: block;
  margin-top: 14px;
  font-size: 10px;
  position: absolute;
}
</style>
