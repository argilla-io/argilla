<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
      :isRequired="isRequired"
      :hasSuggestion="hasSuggestion"
      :tooltipMessage="description"
    />

    <LabelSelectionComponent
      v-model="options"
      :multiple="false"
      :componentId="questionId"
      :isFocused="isFocused"
      :maxOptionsToShowBeforeCollapse="maxOptionsToShowBeforeCollapse"
      @on-focus="onFocus"
    />
  </div>
</template>

<script>
export default {
  name: "SingleLabelComponent",
  props: {
    questionId: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    options: {
      type: Array,
      required: true,
    },
    isRequired: {
      type: Boolean,
      default: () => false,
    },
    isFocused: {
      type: Boolean,
      default: () => false,
    },
    description: {
      type: String,
      default: () => "",
    },
    visibleOptions: {
      type: Number | null,
      required: false,
    },
    hasSuggestion: {
      type: Boolean,
      default: () => false,
    },
  },
  model: {
    prop: "options",
  },
  computed: {
    maxOptionsToShowBeforeCollapse() {
      return this.visibleOptions ?? -1;
    },
  },
  methods: {
    onFocus() {
      this.$emit("on-focus");
    },
  },
  watch: {
    options: {
      deep: true,
      handler(newOptions) {
        const hasAnswer = newOptions.some((option) => option.isSelected);
        hasAnswer && this.$emit("on-user-answer");
      },
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
