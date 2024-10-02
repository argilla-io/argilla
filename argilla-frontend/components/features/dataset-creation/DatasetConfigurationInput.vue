<template>
  <div class="dataset-config__input-container">
    <input
      type="text"
      :value="value"
      @input="onInput($event.target.value)"
      :placeholder="placeholder"
      class="dataset-config__input"
    />
  </div>
</template>

<script>
export default {
  props: {
    value: {
      type: String,
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
    onInput(value) {
      this.$emit("on-value-change", value);
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-config__input-container {
  width: 100%;
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
