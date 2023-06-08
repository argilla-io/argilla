<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
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
  },
  model: {
    prop: "options",
    event: "on-change-rating",
  },
  methods: {
    onChangeRating(newOptions) {
      this.$emit("on-change-rating", newOptions);

      const isAnyRatingSelected = this.isAnyRatingSelected(newOptions);
      if (this.isRequired) {
        this.$emit("on-error", !isAnyRatingSelected);
      }
    },
    isAnyRatingSelected(options) {
      return options.some((option) => option.value);
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
