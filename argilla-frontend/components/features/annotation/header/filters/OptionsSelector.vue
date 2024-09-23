<template>
  <BaseDropdown
    class="option-selector"
    :visible="dropdownIsVisible"
    @visibility="onVisibility"
    v-if="options.length"
  >
    <template slot="dropdown-header">
      {{ value }}<svgicon name="chevron-down" height="8" />
    </template>
    <template slot="dropdown-content">
      <ul class="option-selector__options">
        <li
          :class="
            value === option
              ? 'option-selector__option--selected'
              : 'option-selector__option'
          "
          v-for="option in options"
          :key="option"
          @click="selectOption(option)"
        >
          {{ option }}
        </li>
      </ul>
    </template>
  </BaseDropdown>
</template>

<script>
export default {
  props: {
    value: {
      type: [String, Number],
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
  data() {
    return {
      dropdownIsVisible: false,
    };
  },
  methods: {
    onVisibility(value) {
      this.dropdownIsVisible = value;
    },
    selectOption(option) {
      this.$emit("onValueChange", option);

      this.dropdownIsVisible = false;
    },
  },
};
</script>
<style lang="scss" scoped>
.option-selector {
  padding: calc($base-space / 2);
  user-select: none;
  text-transform: capitalize;
  @include font-size(13px);
  font-weight: 500;
  :deep(.dropdown__content) {
    top: 100%;
  }

  &__options {
    list-style: none;
    min-width: 100px;
    padding: calc($base-space / 2);
    margin: 0;
    &:hover :not(.option-selector__option:hover) {
      background: none;
    }
  }
  &__option {
    padding: calc($base-space / 2);
    border-radius: $border-radius;
    transition: all 0.2s ease-in;
    cursor: pointer;
    &:hover {
      background: var(--bg-opacity-4);
      transition: all 0.2s ease-out;
    }
    &--selected {
      @extend .option-selector__option;
      background: var(--bg-opacity-4);
    }
  }
  .svg-icon {
    flex-shrink: 0;
  }
}
</style>
