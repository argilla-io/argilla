<template>
  <div class="wrapper">
    <QuestionHeaderComponent :question="question" />
    <div class="question__warning" v-if="warningMessage">
      <svgicon name="danger" width="16" height="16" />
      <span v-text="warningMessage" />
    </div>
    <EntityLabelSelectionComponent
      v-if="!isBulkMode && supportedSpanAnnotation"
      v-model="question.answer.options"
      :componentId="question.id"
      :maxOptionsToShowBeforeCollapse="this.question.settings.visible_options"
      :isFocused="isFocused"
      :showShortcutsHelper="showShortcutsHelper"
      :enableShortcuts="enableShortcuts"
      @on-focus="onFocus"
      @on-selected="onSelected"
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
    enableShortcuts: {
      type: Boolean,
      default: () => false,
    },
    isBulkMode: {
      type: Boolean,
      default: () => false,
    },
  },
  computed: {
    supportedSpanAnnotation() {
      return !!CSS.highlights;
    },
    warningMessage() {
      if (!this.supportedSpanAnnotation) {
        return this.$t("spanAnnotation.notSupported");
      } else if (this.isBulkMode) {
        return this.$t("spanAnnotation.bulkMode");
      }
    },
  },
  methods: {
    onFocus() {
      this.$emit("on-focus");
    },
    onSelected() {
      this.$emit("on-user-answer");
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
    color: $black-54;
    @include font-size(13px);
  }
}
</style>
