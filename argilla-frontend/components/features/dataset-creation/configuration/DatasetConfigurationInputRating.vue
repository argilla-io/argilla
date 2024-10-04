<template>
  <div class="dataset-config__input-container">
    <input
      type="number"
      min="2"
      :value="value.length"
      @input="onInput($event.target.value)"
      @focus="$emit('is-focused', true)"
      @blur="$emit('is-focused', false)"
      :placeholder="placeholder"
      class="dataset-config__input"
    />
  </div>
</template>

<script>
export default {
  props: {
    value: {
      type: Array,
      required: true,
    },
    placeholder: {
      type: String,
      default: "",
    },
  },
  model: {
    prop: "value",
    event: "on-value-change",
  },
  computed: {
    namesJoinedByCommas() {
      return this.value.map((item) => item.name).join(", ");
    },
  },
  methods: {
    onInput(inputValue) {
      const valuesArray = Array.from({ length: inputValue }, (_, i) => ({
        value: i + 1,
      }));
      this.$emit("on-value-change", valuesArray);
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-config__input-container {
  width: 100px;
  padding: 0 $base-space;
  border-radius: $border-radius;
  border: 1px solid var(--bg-opacity-10);
  background: var(--bg-accent-grey-1);
  &:focus-within {
    border-color: var(--fg-cuaternary);
  }
}
.dataset-config__input {
  height: calc($base-space * 4 - 2px);
  padding: 0;
  border: none;
  background: none;
  width: 100%;
  outline: none;
  color: var(--fg-secondary);
  @include input-placeholder {
    color: var(--fg-tertiary);
  }
}
</style>
