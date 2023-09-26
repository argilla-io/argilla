<template>
  <BaseRangeMultipleSlider
    :min="metadata.settings.min"
    :max="metadata.settings.max"
    :sliderValues="sliderValues"
    :step="step"
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
      sliderValues: [this.metadata.value.ge, this.metadata.value.le],
      step: this.metadata.isInteger
        ? parseInt(this.metadata.settings.max / 100)
        : this.metadata.settings.max / 100,
    };
  },
  watch: {
    sliderValues() {
      this.metadata.value.ge = this.sliderValues[0];
      this.metadata.value.le = this.sliderValues[1];
    },
  },
};
</script>
