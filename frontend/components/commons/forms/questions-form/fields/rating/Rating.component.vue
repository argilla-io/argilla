<template>
  <RatingShortcuts @on-user-answer="$emit('on-user-answer')">
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
        @on-focus="onFocus"
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
  gap: 12px;
}
</style>
