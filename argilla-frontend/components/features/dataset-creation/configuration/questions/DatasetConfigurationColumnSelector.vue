<template>
  <BaseDropdown
    class="column-selector"
    :visible="dropdownIsVisible"
    @visibility="onVisibility"
    v-if="options.length"
  >
    <template slot="dropdown-header">
      <svgicon name="assign" height="12" />
      Link to column
      <span v-if="!noMapping" class="column-selector__chip" v-text="value" />
    </template>
    <template slot="dropdown-content">
      <ul class="column-selector__options">
        <li
          :class="
            option === value
              ? 'column-selector__option--selected'
              : 'column-selector__option'
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
import "assets/icons/assign";
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
    noMapping() {
      return this.value === "no mapping";
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
.column-selector {
  user-select: none;
  font-weight: 400;

  :deep(.dropdown__header) {
    display: flex;
    gap: $base-space;
    flex-wrap: wrap;
    min-height: $base-space * 4;
    border: none;
    color: var(--fg-cuaternary);
    &:hover {
      background: none;
    }
  }

  :deep(.dropdown__content) {
    bottom: 100%;
    top: auto;
    right: auto;
    min-width: 140px;
  }

  &__options {
    min-width: 100%;
    list-style: none;
    padding: calc($base-space / 2);
    margin: 0;
    max-height: 140px;
    overflow-y: auto;
  }
  &__chip {
    padding: calc($base-space / 2) $base-space;
    border-radius: $border-radius-m;
    background: var(--bg-accent-grey-1);
    color: var(--fg-cuaternary);
    @include font-size(12px);
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
      @extend .column-selector__option;
    }
  }
  .svg-icon {
    flex-shrink: 0;
  }
}
</style>
