<template>
  <MonoSelectionComponent
    :title="title"
    :initialOutputs="initialOutputs"
    :isRequired="isRequired"
    :isIcon="tooltipMessage"
    :tooltipMessage="tooltipMessage"
    :colorHighlight="colorHighlight"
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
    onChangeSingleLabel(newOutputs) {
      this.$emit("on-change-single-label", newOutputs);
      const isAnySingleLabelSelected =
        this.isAnySingleLabelSelected(newOutputs);

      if (this.isRequired) {
        this.$emit("on-error", !isAnySingleLabelSelected);
      }
    },
    isAnySingleLabelSelected(outputs) {
      return outputs.some((output) => output.value);
    },
  },
};
</script>
