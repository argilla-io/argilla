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
      sliderValues: [this.metadata.value.ge, this.metadata.value.le],
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
