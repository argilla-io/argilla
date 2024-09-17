<template>
  <BaseDropdown
    class="similarity-config"
    :class="useTextCapitalized ? '--capitalized' : ''"
    :visible="dropdownIsVisible"
    @visibility="onVisibility"
    v-if="options.length"
  >
    <template slot="dropdown-header">
      {{ useExtraText }}
      {{ selectedValue }}
      <svgicon name="chevron-down" height="8" />
    </template>
    <template slot="dropdown-content">
      <ul class="similarity-config__options">
        <li
          :class="
            value === getKeyProp(option)
              ? 'similarity-config__option--selected'
              : 'similarity-config__option'
          "
          v-for="option in options"
          :key="getKeyProp(option)"
          @click="selectOption(getKeyProp(option))"
        >
          {{ getDisplayProp(option) }}
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
    useTextCapitalized: {
      type: Boolean,
      default: true,
    },
    useExtraText: {
      type: String,
    },
    useTextProp: {
      type: String,
    },
    useKeyProp: {
      type: String,
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
        (option) => this.value === this.getKeyProp(option)
      );

      return this.getDisplayProp(selectedOption);
    },
  },
  methods: {
    getDisplayProp(option) {
      if (this.useTextProp) {
        return option[this.useTextProp];
      }
      return option;
    },
    getKeyProp(option) {
      if (this.useKeyProp) {
        return option[this.useKeyProp];
      }
      return option;
    },
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
.similarity-config {
  user-select: none;
  font-weight: 500;

  &__options {
    min-width: 100px;
    list-style: none;
    padding: calc($base-space / 2);
    margin: 0;
    &:hover :not(.similarity-config__option:hover) {
      background: none;
    }
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
      @extend .similarity-config__option;
      background: var(--bg-opacity-4);
    }
  }
  .svg-icon {
    flex-shrink: 0;
  }
}
</style>
