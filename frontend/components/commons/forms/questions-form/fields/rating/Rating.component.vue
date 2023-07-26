<template>
  <RatingShortcuts>
    <div class="wrapper">
      <QuestionHeaderComponent
        :title="title"
        :hasSuggestion="hasSuggestion"
        :isRequired="isRequired"
        :tooltipMessage="description"
      />

      <RatingMonoSelectionComponent
        ref="ratingMonoSelectionRef"
        v-model="options"
        :isFocused="isFocused"
        @on-focus="$emit('on-focus')"
      />
    </div>
  </RatingShortcuts>
</template>

<script>
export default {
  name: "RatingComponent",
  props: {
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
    hasSuggestion: {
      type: Boolean,
      default: () => false,
    },
  },
  model: {
    prop: "options",
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
