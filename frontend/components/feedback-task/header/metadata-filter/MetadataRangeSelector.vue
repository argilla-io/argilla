<template>
  <BaseRangeMultipleSlider
    :min="metadata.settings.min"
    :max="metadata.settings.max"
    v-model="sliderValues"
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
      step: this.metadata.isInteger ? 1 : 0.01,
    };
  },
  watch: {
    sliderValues() {
      this.metadata.value.ge = this.parse(this.sliderValues[0]);
      this.metadata.value.le = this.parse(this.sliderValues[1]);
    },
  },
  methods: {
    parse(value) {
      return this.metadata.isInteger ? parseInt(value) : parseFloat(value);
    },
  },
};
</script>
