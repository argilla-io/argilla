<template>
  <ul class="chip-selector__options">
    <li
      class="chip-selector__option"
      v-for="(option, index) in options"
      :key="option.value"
      @click="selectOption(option)"
    >
      <input
        class="chip-selector__input"
        :id="index"
        type="radio"
        :checked="option.value === value.value"
        @change="selectOption(option)"
      />
      <label :for="index">{{ option }}</label>
    </li>
  </ul>
</template>

<script>
export default {
  props: {
    value: {
      type: [Object, String],
      required: true,
    },
    options: {
      type: Array,
      required: true,
    },
  },
  model: {
    prop: "value",
    event: "onValueChange",
  },
  methods: {
    selectOption(option) {
      this.$emit("onValueChange", option);
    },
  },
};
</script>
<style lang="scss" scoped>
.chip-selector {
  &__options {
    display: flex;
    flex-wrap: wrap;
    gap: $base-space;
    padding: 0;
    margin: $base-space 0 0 0;
  }
  &__option {
    list-style: none;
  }
  &__input {
    position: absolute;
    opacity: 0;
    width: 1px;
    height: 1px;
    margin: -1px;
    border: 1px solid var(--fg-opacity-4);
    & + label {
      display: inline-block;
      padding: calc($base-space / 2) $base-space;
      border-radius: $border-radius-m;
      background-color: var(--bg-accent-grey-3);
      cursor: pointer;
      transition: all 0.2s ease-in;
      border: 1px solid var(--bg-opacity-10);
      @include font-size(12px);
      &:hover {
        border-color: var(--bg-opacity-20);
      }
    }
    &:checked + label {
      border-color: var(--fg-cuaternary);
      color: var(--fg-cuaternary);
      background: var(--bg-accent-grey-1);
    }
  }
}
</style>
