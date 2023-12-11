<template>
  <div class="page-size__wrapper">
    <p class="page-size__text" v-text="`${$t('records-per-page')}:`" />
    <BaseDropdown
      class="page-size"
      :visible="dropdownIsVisible"
      @visibility="onVisibility"
      v-if="options.length"
    >
      <template slot="dropdown-header">
        <p class="page-size__text" v-text="selectedValue" />
        <svgicon name="chevron-down" height="8" />
      </template>
      <template slot="dropdown-content">
        <ul class="page-size__options">
          <li
            :class="'page-size__option'"
            v-for="option in options"
            :key="option"
            @click="selectOption(option)"
          >
            {{ option }}
          </li>
        </ul>
      </template>
    </BaseDropdown>
  </div>
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
.page-size {
  user-select: none;
  cursor: pointer;
  &:hover {
    .page-size__text {
      color: $black-54;
    }
  }
  &__wrapper {
    display: flex;
    align-items: center;
    gap: $base-space;
  }

  &__options {
    min-width: 100px;
    list-style: none;
    padding: calc($base-space / 2);
    margin: 0;
    &:hover :not(.page-size__option:hover) {
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
      background: $black-4;
      transition: all 0.2s ease-out;
    }
    &--selected {
      @extend .page-size__option;
      background: $black-4;
    }
  }
  &__text {
    @include font-size(13px);
    font-weight: 400;
    color: $black-37;
    margin: 0;
  }
  .svg-icon {
    flex-shrink: 0;
  }
}
</style>
