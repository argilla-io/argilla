<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
      :hasSuggestion="hasSuggestion"
      :isRequired="isRequired"
      :tooltipMessage="description"
    />

    <RatingMonoSelectionComponent v-model="options" />
  </div>
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
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
