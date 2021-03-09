<template>
  <span>
    {{ numericValue }}<span>{{ type }}</span>
    <slot />
    <span v-if="percent">%</span>
  </span>
</template>

<script>
export default {
  props: {
    value: {
      type: Number,
      default: undefined,
    },
    type: {
      type: String,
      default: undefined,
    },
    decimals: {
      type: Number,
      default: 2,
    },
    percent: {
      type: Boolean,
      default: false,
    },
  },
  data: () => ({}),
  computed: {
    numericValue() {
      if (this.percent === true) {
        const v = this.value * 100;
        if (v % 1 === 0) {
          return v;
        }
        return v.toFixed(this.decimals);
      }
      return this.value.toFixed(this.decimals);
    },
  },
};
</script>
