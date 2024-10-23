<template>
  <div class="dataset-config-rating__input-container">
    <input
      type="number"
      min="0"
      max="10"
      step="1"
      :value="value.length - 1"
      @input="onInput($event.target.value)"
      @focus="$emit('is-focused', true)"
      @blur="$emit('is-focused', false)"
      :placeholder="placeholder"
      class="dataset-config-rating__input"
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
  methods: {
    onInput(inputValue) {
      const valuesArray = Array.from(
        { length: parseInt(inputValue) + 1 },
        (_, i) => ({
          value: i,
        })
      );

      this.$emit("on-value-change", valuesArray);
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-config-rating__input-container {
  width: 100px;
  padding: 0 $base-space;
  border-radius: $border-radius;
  border: 1px solid var(--bg-opacity-10);
  background: var(--bg-accent-grey-1);
  &:focus-within {
    border-color: var(--fg-cuaternary);
  }
}
.dataset-config-rating__input {
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
