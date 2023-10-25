<template>
  <SimilarityConfigDropdown v-model="selected" :options="[10, 50, 100, 200]" />
</template>
<script>
export default {
  props: {
    value: {
      type: Number,
      required: true,
    },
  },
  model: {
    prop: "value",
    event: "onValueChanged",
  },
  data() {
    return {
      selected: this.value,
    };
  },
  watch: {
    selected() {
      this.$emit("onValueChanged", this.selected);
    },
  },
};
</script>
