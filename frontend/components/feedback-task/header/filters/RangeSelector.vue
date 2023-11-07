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
      sliderValues: [this.filter.value.ge, this.filter.value.le],
      step: this.filter.isInteger ? 1 : 0.01,
    };
  },
  watch: {
    sliderValues() {
      this.filter.value.ge = this.parse(this.sliderValues[0]);
      this.filter.value.le = this.parse(this.sliderValues[1]);
    },
  },
  methods: {
    parse(value) {
      return this.filter.isInteger ? parseInt(value) : parseFloat(value);
    },
  },
};
</script>
