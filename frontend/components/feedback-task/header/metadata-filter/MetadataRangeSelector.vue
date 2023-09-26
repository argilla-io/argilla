<template>
  <BaseRangeMultipleSlider
    :min="metadata.settings.min"
    :max="metadata.settings.max"
    :sliderValues="sliderValues"
  />
</template>
<script>
export default {
  props: {
    metadata: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      sliderValues: [this.metadata.value.from, this.metadata.value.to],
    };
  },
  watch: {
    sliderValues() {
      this.metadata.value.from = this.sliderValues[0];
      this.metadata.value.to = this.sliderValues[1];
    },
  },
};
</script>
