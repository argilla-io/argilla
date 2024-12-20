<template>
  <BaseDropdown
    class="add-question-selector"
    :visible="dropdownIsVisible"
    @visibility="onVisibility"
    v-if="options.length"
  >
    <template slot="dropdown-header">
      <BaseButton
        class="add-question-selector__button"
        :aria-label="$t('config.addQuestion')"
        ><span class="add-question-selector__button-icon"
          ><svgicon name="plus" aria-hidden="true" /></span
      ></BaseButton>
    </template>
    <template slot="dropdown-content">
      <ul class="add-question-selector__options">
        <li
          class="add-question-selector__option"
          v-for="option in options"
          :key="option"
          @click="selectOption(option)"
        >
          {{ $t(`config.question.${option}`) }}
        </li>
      </ul>
    </template>
  </BaseDropdown>
</template>

<script>
import "assets/icons/plus";
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
    top: 0;
    left: auto;
    right: calc(100% + $base-space);
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
