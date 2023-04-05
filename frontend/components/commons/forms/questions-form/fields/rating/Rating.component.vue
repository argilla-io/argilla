<template>
  <MonoSelectionComponent
    :title="title"
    :initialOutputs="initialOutputs"
    :isRequired="isRequired"
    :colorHighlight="colorHighlight"
    backgroundColor="#d8d8fa"
    borderColor="#aaaadd"
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
    colorHighlight: {
      type: String,
      default: () => "black",
    },
  },
};
</script>
