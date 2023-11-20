<template>
  <SimilarityConfigDropdown
    v-if="selected && vectors.length > 1"
    v-model="selected"
    :options="vectors"
    :useExtraText="$t('with')"
    :useTextCapitalized="false"
    useTextProp="title"
    useKeyProp="name"
  />
</template>
<script>
export default {
  props: {
    value: {
      type: String,
    },
    vectors: {
      type: Array,
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
