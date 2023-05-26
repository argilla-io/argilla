<template>
  <MonoSelectionComponent
    :initialOptions="initialOptions"
    @on-change="onChangeSingleLabel"
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
    tooltipMessage: {
      type: String,
      default: () => "",
    },
  },
  methods: {
    onChangeSingleLabel(newOptions) {
      this.$emit("on-change-single-label", newOptions);
      const isAnySingleLabelSelected =
        this.isAnySingleLabelSelected(newOptions);

      if (this.isRequired) {
        this.$emit("on-error", !isAnySingleLabelSelected);
      }
    },
    isAnySingleLabelSelected(options) {
      return options.some((option) => option.value);
    },
  },
};
</script>
