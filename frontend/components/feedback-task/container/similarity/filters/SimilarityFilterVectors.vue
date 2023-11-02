<template>
  <div>
    <BaseRadioButton
      v-for="vector in vectors"
      :key="vector.id"
      :id="vector.name"
      :value="vector.name"
      v-model="selected"
    >
      {{ vector.title }}
    </BaseRadioButton>
  </div>
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
    selected() {
      this.$emit("onValueChanged", this.selected);
    },
  },
};
</script>
