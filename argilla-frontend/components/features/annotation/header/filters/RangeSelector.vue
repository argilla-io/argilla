<template>
  <BaseRangeMultipleSlider
    :min="filter.settings.min"
    :max="filter.settings.max"
    v-model="sliderValues"
    :step="step"
  />
</template>
<script>
export default {
  props: {
    filter: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      sliderValues: [this.filter.rangeValue.ge, this.filter.rangeValue.le],
      step: this.filter.isInteger ? 1 : 0.01,
    };
  },
  watch: {
    sliderValues() {
      this.filter.rangeValue.ge = this.parse(this.sliderValues[0]);
      this.filter.rangeValue.le = this.parse(this.sliderValues[1]);
    },
  },
  methods: {
    parse(value) {
      return this.filter.isInteger ? parseInt(value) : parseFloat(value);
    },
  },
};
</script>
