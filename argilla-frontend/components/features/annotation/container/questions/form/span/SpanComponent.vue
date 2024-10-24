<template>
  <div class="wrapper">
    <QuestionHeaderComponent :question="question" />
    <div class="question__warning" v-if="warningMessage">
      <svgicon name="danger" width="16" height="16" />
      <span v-text="warningMessage" />
    </div>
    <EntityLabelSelectionComponent
      v-if="supportedSpanAnnotation"
      v-model="question.answer.options"
      :visible-shortcuts="visibleShortcuts"
      :componentId="question.id"
      :maxOptionsToShowBeforeCollapse="this.question.settings.visible_options"
      :isFocused="isFocused"
      :showShortcutsHelper="showShortcutsHelper"
      :enableSpanQuestionShortcutsGlobal="enableSpanQuestionShortcutsGlobal"
      @on-focus="onFocus"
    />
  </div>
</template>

<script>
import "assets/icons/danger";
export default {
  name: "SpanComponent",
  props: {
    question: {
      type: Object,
      required: true,
    },
    isFocused: {
      type: Boolean,
      default: () => false,
    },
    showShortcutsHelper: {
      type: Boolean,
      default: () => false,
    },
    enableSpanQuestionShortcutsGlobal: {
      type: Boolean,
      default: () => false,
    },
    isBulkMode: {
      type: Boolean,
      default: () => false,
    },
    visibleShortcuts: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    supportedSpanAnnotation() {
      return !!CSS.highlights;
    },
    warningMessage() {
      if (!this.supportedSpanAnnotation) {
        return this.$t("spanAnnotation.notSupported");
      }
    },
  },
  methods: {
    onFocus() {
      this.$emit("on-focus");
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: $base-space;
}
.question {
  &__warning {
    display: flex;
    align-items: center;
    gap: $base-space;
    color: var(--fg-secondary);
    @include font-size(13px);
  }
}
</style>
