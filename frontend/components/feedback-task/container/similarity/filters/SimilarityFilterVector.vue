<template>
  <SimilarityConfigDropdown
    v-if="selected && availableVectors.length > 1"
    v-model="selected"
    :options="availableVectors"
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
    availableVectors: {
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
    selected() {
      this.$emit("onValueChanged", this.selected);
    },
  },
};
</script>
