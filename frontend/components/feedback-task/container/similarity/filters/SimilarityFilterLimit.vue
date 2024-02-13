<template>
  <SimilarityConfigDropdown
    :data-title="$t('similarity.record-number')"
    v-model="selected"
    :options="[10, 50, 100, 200]"
  />
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
    value(newValue) {
      this.selected = newValue;
    },
    selected() {
      this.$emit("onValueChanged", this.selected);
    },
  },
};
</script>

<style lang="scss" scoped>
[data-title] {
  position: relative;
  overflow: visible;
  @include tooltip-mini("top");
  &:after {
    right: 0;
  }
}
</style>
