<template>
  <div :class="isButtonActive ? 'filter-button--active' : 'filter-button'">
    <BaseButton class="filter-button__button" v-if="!showIcon">{{
      buttonName
    }}</BaseButton>
    <svgicon v-else :name="iconName" width="16" height="16" />
    <slot></slot>
    <svgicon
      class="filter-button__chevron"
      name="chevron-down"
      width="16"
      height="16"
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
      required: true,
    },
    showIcon: {
      type: Boolean,
      default: false,
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
  height: $base-space * 5;
  padding: $base-space 12px;
  border-radius: $border-radius;
  background: none;
  transition: background-color 0.2s ease;
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
  }
  & > * {
    flex-shrink: 0;
  }
}
</styles>
