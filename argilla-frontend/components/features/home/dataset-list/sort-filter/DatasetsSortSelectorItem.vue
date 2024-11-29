<template>
  <div class="sort-selector-item">
    <BaseDropdown
      :visible="visibleDropdown"
      @visibility="onToggleVisibility"
      class="sort-selector-item__dropdown"
    >
      <span slot="dropdown-header" class="sort-selector-item__dropdown__header">
        <div class="sort-selector-item__dropdown__header__item">
          <span
            class="sort-selector-item__dropdown__header__text"
            title="category.title"
            v-text="selectedOptionLabel"
          />
        </div>
        <svgicon width="12" height="12" name="chevron-down" />
      </span>
      <ul slot="dropdown-content" class="sort-selector-item__list">
        <li v-for="option in filteredOptions" :key="option.value">
          <BaseButton
            class="sort-selector-item__list__item"
            @click="changeField(option.value)"
            >{{ option.label }}</BaseButton
          >
        </li>
      </ul>
    </BaseDropdown>
    <BaseButton
      title="sort direction"
      class="sort-selector-item__direction secondary clear"
      @click="changeDirection(selectedDirection === 'asc' ? 'desc' : 'asc')"
    >
      <svgicon
        width="16"
        height="16"
        :name="selectedDirection === 'asc' ? 'arrow-up' : 'arrow-down'"
        :aria-label="
          'Change sort direction to ' +
          (selectedDirection === 'asc' ? 'up' : 'down')
        "
      />
    </BaseButton>
  </div>
</template>

<script>
import "assets/icons/arrow-up";
import "assets/icons/arrow-down";
import "assets/icons/chevron-down";
export default {
  props: {
    options: {
      type: Array,
      required: true,
    },
    selectedOption: {
      type: String,
      required: true,
    },
    selectedDirection: {
      type: String,
      required: true,
    },
  },
  data: () => {
    return {
      visibleDropdown: false,
    };
  },
  computed: {
    filteredOptions() {
      return this.options.filter((option) => option !== this.selectedOption);
    },
    selectedOptionLabel() {
      return this.options.find((option) => option.value === this.selectedOption)
        ?.label;
    },
  },
  methods: {
    onToggleVisibility(value) {
      this.visibleDropdown = value;
    },
    changeDirection(dir) {
      this.$emit("change-sort-direction", dir);
    },
    changeField(field) {
      this.$emit("change-sort-field", field);
      this.visibleDropdown = false;
    },
  },
};
</script>
<style lang="scss" scoped>
.sort-selector-item {
  display: flex;
  align-items: center;
  gap: $base-space;
  padding: $base-space * 2;
  &__dropdown {
    width: 100%;
    min-width: 0;
    &__header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-direction: row;
      width: 100%;
      padding: calc($base-space / 2) $base-space;
      border: 1px solid var(--bg-opacity-10);
      border-radius: $border-radius;
      cursor: pointer;
      &__item {
        display: flex;
        flex-direction: column;
        width: 90%;
      }
      &__group {
        margin-top: calc($base-space / 2 * -1);
        color: var(--fg-tertiary);
        @include font-size(10px);
        text-transform: capitalize;
      }
      &__text {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .svg-icon {
        flex-shrink: 0;
      }
    }
  }
  &__list {
    padding: calc($base-space / 2);
    list-style: none;
    width: 100%;
    margin: 0;
    &__item {
      width: 100%;
      padding: $base-space;
      justify-content: space-between;
      border-radius: $border-radius;
      font-weight: 500;
      span {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        @include line-height(16px);
        font-weight: 400;
      }
      &:hover {
        background: var(--bg-opacity-4);
      }
      &:focus {
        outline: none;
      }
    }
  }
  &__close-button {
    flex-shrink: 0;
    padding: $base-space;
  }
  &__direction {
    flex-shrink: 0;
    padding: $base-space;
  }
  :deep(.dropdown__content) {
    width: 100%;
  }
}
</style>
