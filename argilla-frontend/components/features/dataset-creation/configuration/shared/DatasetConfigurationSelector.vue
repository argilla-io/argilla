<template>
  <BaseDropdown
    class="selector"
    :visible="dropdownIsVisible"
    @visibility="onVisibility"
    v-if="options.length"
  >
    <template slot="dropdown-header">
      {{ value?.name ?? value ?? "Select workspace" }}
      <svgicon name="chevron-down" height="8" />
    </template>
    <template slot="dropdown-content">
      <slot name="optionsIntro" />
      <ul class="selector__options">
        <li
          :class="
            option === value ? 'selector__option--selected' : 'selector__option'
          "
          v-for="(option, index) in filteredOptions"
          :key="index"
          @click="selectOption(option)"
        >
          {{ option?.name ?? option }}
        </li>
      </ul>
    </template>
  </BaseDropdown>
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
  data() {
    return {
      dropdownIsVisible: false,
    };
  },
  computed: {
    filteredOptions() {
      return this.options.filter(
        (option) => JSON.stringify(option) !== JSON.stringify(this.value)
      );
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
    justify-content: space-between;
    height: $base-space * 4;
    padding: 0 $base-space;
    background: var(--bg-opacity-4);
    border: none;
  }

  :deep(.dropdown__content) {
    min-width: 100%;
  }

  &__options {
    min-width: 100%;
    list-style: none;
    padding: calc($base-space / 2);
    margin: 0;
    max-height: 120px;
    overflow-y: auto;
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
