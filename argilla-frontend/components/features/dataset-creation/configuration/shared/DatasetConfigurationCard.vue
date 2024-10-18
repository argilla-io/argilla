<template>
  <div class="config-card__wrapper">
    <div class="config-card">
      <div class="config-card__content" :class="item.type.replace(/ /g, '')">
        <h3 class="config-card__title">
          <svgicon
            class="config-card__icon"
            width="6"
            name="draggable"
            color="var(--bg-opacity-20)"
          />{{ item.name }}
          <span v-if="item.dtype" class="config-card__dtype">{{
            item.dtype
          }}</span>
        </h3>
        <slot name="header" />
        <div class="config-card__row">
          <DatasetConfigurationChipsSelector
            :id="item.name"
            :type="configType"
            class="config-card__type"
            :options="availableTypes"
            @onValueChange="$emit('change-type', $event)"
            v-model="item.type"
          />
        </div>
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script>
import "assets/icons/draggable";
export default {
  props: {
    item: {
      type: Object,
      required: true,
    },
    configType: {
      type: String,
      required: true,
    },
    availableTypes: {
      type: Array,
      required: true,
    },
    removeIsAllowed: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    hasNoMapping() {
      return this.item.type.value === "no mapping";
    },
  },
  model: {
    prop: "type",
    event: "change",
  },
};
</script>

<style lang="scss" scoped>
$validate-color: hsl(216, 55%, 54%);
$error-color: hsl(3, 100%, 69%);
$no-mapping-color: hsl(0, 0%, 50%);
.config-card {
  $this: &;
  position: relative;
  border-radius: $base-space * 2;
  border: 1px solid hsl(from var(--bg-config-card) h s 86%);
  background: var(--bg-config-card);
  transition: all 0.3s ease-in;
  &__wrapper {
    border-radius: $base-space * 2;
    background: var(--bg-accent-grey-1);
    transition: all 0.3s ease-in;
    cursor: pointer;
    &:hover {
      transition: all 0.2s ease-in;
      box-shadow: 0 0 3px 1px var(--bg-opacity-10);
      .config-card__icon {
        opacity: 1;
      }
    }
  }
  &__content {
    padding: $base-space * 2;
    display: flex;
    flex-direction: column;
    gap: $base-space;
  }
  &__title {
    display: flex;
    gap: $base-space;
    align-items: center;
    margin: 0;
    font-weight: 500;
    @include font-size(14px);
  }
  &__icon {
    position: absolute;
    left: 6px;
    top: 19px;
    opacity: 0;
  }
  &__dtype {
    font-family: monospace, monospace;
    color: var(--fg-secondary);
    font-weight: 400;
    @include font-size(10px);
  }
  &__row {
    display: flex;
    align-items: center;
    gap: $base-space;
    width: 100%;
  }
  &__type {
    flex: 1;
  }
  :deep(.chip-selector__input + label) {
    background: hsl(from var(--bg-accent-grey-1) h s l / 60%);
    border-color: hsl(from var(--bg-config-card) h s 86%);
  }
  :deep(.chip-selector__input:checked + label) {
    background: var(--bg-accent-grey-1);
  }
  &:has(.nomapping) {
    border-color: var(--bg-opacity-10);
    background: hsl(from var(--bg-config-card) h 40% 96%);
    :deep(.chip-selector__input + label) {
      background: hsl(from var(--bg-accent-grey-1) h s l / 50%);
      border-color: var(--bg-opacity-10);
    }
    :deep(.chip-selector__input:checked + label) {
      background: var(--bg-accent-grey-1);
    }
  }
  &:has(.error) {
    background: hsla(from $error-color h s l / 0.16);
  }
  &:deep(.re-switch-label) {
    @include font-size(13px);
  }
}
</style>
