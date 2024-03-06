<template>
  <div class="wrapper">
    <QuestionHeaderComponent :question="question" />
    <EntityLabelSelectionComponent
      v-model="question.answer.options"
      :componentId="question.id"
      :maxOptionsToShowBeforeCollapse="maxOptionsToShowBeforeCollapse"
      :isFocused="isFocused"
      :showShortcutsHelper="showShortcutsHelper"
      @on-focus="onFocus"
      @on-selected="onSelected"
    />
  </div>
</template>

<script>
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
  },
  computed: {
    maxOptionsToShowBeforeCollapse() {
      return this.question.settings.visible_options ?? -1;
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
</style>
