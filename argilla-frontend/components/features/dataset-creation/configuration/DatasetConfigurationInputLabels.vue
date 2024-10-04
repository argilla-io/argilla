<template>
  <div class="dataset-config__input-container">
    <input
      type="text"
      :value="namesJoinedByCommas"
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
    // Usa una propiedad computada para unir los nombres por comas
    namesJoinedByCommas() {
      return this.value.map((item) => item.name).join(", ");
    },
  },
  methods: {
    onInput(inputValue) {
      const namesArray = inputValue
        .split(",")
        .map((name) => ({ name: name.trim() }));
      this.$emit("on-value-change", namesArray);
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
