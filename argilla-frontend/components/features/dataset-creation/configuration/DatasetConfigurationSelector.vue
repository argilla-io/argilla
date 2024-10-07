<template>
  <BaseDropdown
    class="selector"
    :visible="dropdownIsVisible"
    @visibility="onVisibility"
    v-if="options.length"
  >
    <template slot="dropdown-header">
      {{ selectedValue }}
      <svgicon name="chevron-down" height="8" />
    </template>
    <template slot="dropdown-content">
      <ul class="selector__options">
        <li
          :class="
            option === selectedValue
              ? 'selector__option--selected'
              : 'selector__option'
          "
          v-for="option in filteredOptions"
          :key="option.value"
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
  computed: {
    filteredOptions() {
      return this.options.filter((option) => option.value !== this.value.value);
    },
    selectedValue() {
      return this.options.find((option) => this.value.value === option.value);
    },
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
.selector {
  user-select: none;
  font-weight: 400;

  :deep(.dropdown__header) {
    background: var(--bg-accent-grey-1);
    justify-content: space-between;
    height: $base-space * 4;
    padding: 0 $base-space;
    border: 1px solid var(--bg-opacity-10);
  }

  :deep(.dropdown__content) {
    min-width: 100%;
  }

  &__options {
    min-width: 100%;
    list-style: none;
    padding: calc($base-space / 2);
    margin: 0;
  }
  &__option {
    padding: calc($base-space / 2);
    border-radius: $border-radius;
    transition: all 0.2s ease-in;
    width: max-content;
    min-width: 100%;
    cursor: pointer;
    &:hover {
      background: var(--bg-opacity-4);
      transition: all 0.2s ease-out;
    }
    &--selected {
      background: var(--bg-opacity-4);
      @extend .selector__option;
    }
  }
  .svg-icon {
    flex-shrink: 0;
  }
}
</style>
