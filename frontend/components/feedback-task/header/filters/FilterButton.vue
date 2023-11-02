<template>
  <div :class="isButtonActive ? 'filter-button--active' : 'filter-button'">
    <svgicon v-if="iconName" :name="iconName" width="16" height="16" />
    <BaseButton class="filter-button__button">{{ buttonName }}</BaseButton>
    <slot></slot>
    <svgicon
      v-if="showChevronIcon"
      class="filter-button__chevron"
      name="chevron-down"
      width="8"
      height="8"
    />
  </div>
</template>

<script>
import "assets/icons/chevron-down";
import "assets/icons/sort";
export default {
  props: {
    buttonName: {
      type: String,
      required: true,
    },
    iconName: {
      type: String,
    },
    showChevronIcon: {
      type: Boolean,
      default: true,
    },
    isButtonActive: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<styles lang="scss" scoped>
.filter-button {
  display: flex;
  gap: $base-space;
  align-items: center;
  width: max-content;
  min-height: $base-space * 4;
  padding: $base-space;
  border-radius: $border-radius;
  background: none;
  transition: background-color 0.2s ease;
  line-height: 1;
  cursor: pointer;
  &:hover,
  &--active {
    background: $black-4;
    @extend .filter-button;
  }
  &--active {
    &:hover {
      background: $black-6;
    }
  }
  &__button.button {
    padding: 0;
    border-radius: 0;
    @include font-size(14px);
  }
  & > * {
    flex-shrink: 0;
  }
}
</styles>
