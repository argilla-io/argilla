<template>
  <MonoSelectionComponent
    :title="title"
    :initialOutputs="initialOutputs"
    :isRequired="isRequired"
    :isIcon="tooltipMessage"
    :tooltipMessage="tooltipMessage"
    :colorHighlight="colorHighlight"
    @on-change="$emit('on-change-rating', $event)"
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
};
</script>
