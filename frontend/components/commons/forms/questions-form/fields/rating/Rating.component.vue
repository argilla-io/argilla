<template>
  <MonoSelectionComponent
    :title="title"
    :initialOutputs="initialOutputs"
    :isRequired="isRequired"
    :colorHighlight="colorHighlight"
    :isIcon="isIcon"
    :tooltipMessage="tooltipMessage"
    backgroundColor="#d8d8fa"
    borderColor="#aaaadd"
    @on-change="onChangeRating"
  />
</template>

<script>
export default {
  name: "RatingComponent",
  props: {
    title: {
      type: String,
      required: true,
    },
    initialOutputs: {
      type: Array,
      required: true,
    },
    isRequired: {
      type: Boolean,
      default: () => false,
    },
    isIcon: {
      type: Boolean,
      default: () => false,
    },
    tooltipMessage: {
      type: String,
      default: () => "",
    },
    colorHighlight: {
      type: String,
      default: () => "black",
    },
  },
  methods: {
    onChangeRating(newOutputs) {
      this.$emit("on-change-rating", newOutputs);
      const isAnyRatingSelected = this.isAnyRatingSelected(newOutputs);

      if (this.isRequired) {
        this.$emit("on-error", !isAnyRatingSelected);
      }
    },
    isAnyRatingSelected(outputs) {
      return outputs.some((output) => output.value);
    },
  },
};
</script>
