<template>
  <MonoSelectionComponent
    :title="title"
    :initialOptions="initialOptions"
    :isRequired="isRequired"
    :colorHighlight="colorHighlight"
    :isIcon="isIcon"
    :tooltipMessage="tooltipMessage"
    backgroundColor="#E0E0FF"
    borderColor="#CDCDFF"
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
    initialOptions: {
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
