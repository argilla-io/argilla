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
  computed: {
    selectedValue() {
      const selectedOption = this.options.find(
        (option) => this.value === option
      );

      return selectedOption;
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
  font-weight: 500;

  &__options {
    min-width: 100px;
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
    }
  }
  .svg-icon {
    flex-shrink: 0;
  }
}
</style>
