<template>
  <div>
    <BaseRadioButton
      v-for="vector in vectors"
      :key="vector.id"
      :id="vector.id"
      :value="vector.id"
      v-model="selected"
      @click="onChanged(vector.id)"
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
      selected: null,
    };
  },
  watch: {
    value(newSelected) {
      this.selected = newSelected;
    },
  },
  mounted() {
    if (!this.value) {
      this.$emit("onValueChanged", this.vectors[0].id);
    }
  },
  methods: {
    onChanged(vectorId) {
      this.$emit("onValueChanged", vectorId);
    },
  },
};
</script>
