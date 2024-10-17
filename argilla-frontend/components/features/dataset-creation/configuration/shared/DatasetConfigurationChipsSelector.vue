<template>
  <ul class="chip-selector__options">
    <li
      class="chip-selector__option"
      v-for="option in options"
      :key="`${id}-${option.value}`"
      @click="selectOption(option)"
    >
      <input
        class="chip-selector__input"
        :id="`${id}-${option.value}`"
        type="radio"
        :checked="option.value === value.value"
        @change="selectOption(option)"
      />
      <label :for="`${id}-${option.value}`">{{
        $t(`config.${type}.${option}`)
      }}</label>
    </li>
  </ul>
</template>

<script>
export default {
  props: {
    id: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      required: true,
    },
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
      background: hsl(from var(--bg-accent-grey-1) h s l / 80%);
      cursor: pointer;
      transition: all 0.2s ease-in;
      border: 1px solid hsl(from var(--bg-accent-grey-1) h s l / 80%);
      @include font-size(12px);
      &:hover {
        border-color: var(--bg-opacity-20);
      }
    }
    &:checked + label {
      border-color: var(--fg-cuaternary) !important;
      color: var(--fg-cuaternary) !important;
      background: var(--bg-accent-grey-1) !important;
    }
  }
}
</style>
