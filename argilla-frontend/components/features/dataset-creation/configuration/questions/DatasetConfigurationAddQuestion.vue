<template>
  <BaseDropdown
    class="add-question-selector"
    :visible="dropdownIsVisible"
    @visibility="onVisibility"
    v-if="options.length"
  >
    <template slot="dropdown-header">
      <BaseButton class="add-question-selector__button"
        ><span class="add-question-selector__button-icon"
          ><svgicon name="plus" /></span
        >Add Question</BaseButton
      >
    </template>
    <template slot="dropdown-content">
      <ul class="add-question-selector__options">
        <li
          class="add-question-selector__option"
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
    options: {
      type: Array,
      required: true,
    },
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
      this.$emit("add-question", option, option);

      this.dropdownIsVisible = false;
    },
  },
};
</script>
<style lang="scss" scoped>
.add-question-selector {
  margin-right: auto;
  user-select: none;
  font-weight: 500;
  &__button {
    padding: 0;
    color: var(--fg-primary);
  }
  &__button-icon {
    padding: $base-space;
    border-radius: $border-radius;
    border: 1px dashed var(--bg-opacity-20);
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
  }
}
</style>
