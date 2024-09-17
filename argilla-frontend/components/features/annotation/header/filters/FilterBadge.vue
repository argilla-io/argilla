<template>
  <component
    :class="[
      clickable ? 'badge--clickable' : 'badge',
      activeBadge ? 'badge--active' : 'badge',
    ]"
    :is="renderComponent"
    @click="onClick($event)"
    ><span class="badge__text">{{ text }}</span>
    <BaseButton
      v-if="clearable"
      class="badge__close-button"
      @click="onClear($event)"
    >
      <svgicon
        class="badge__close-button__icon"
        name="close"
        width="10"
        height="10"
    /></BaseButton>
  </component>
</template>

<script>
import "assets/icons/close";
export default {
  props: {
    text: {
      type: String,
      required: true,
    },
    activeBadge: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      renderComponent: "p",
      clickable: false,
      clearable: false,
    };
  },
  mounted() {
    if (this.$listeners["on-click"]) {
      this.clickable = true;
      this.renderComponent = "baseButton";
    }
    if (this.$listeners["on-clear"]) {
      this.clearable = true;
    }
  },
  methods: {
    onClick($event) {
      this.$emit("on-click", $event);
    },
    onClear($event) {
      this.$emit("on-clear", $event);
    },
  },
};
</script>

<style lang="scss" scoped>
$badgeBgColor: var(--bg-filter-badge);
$badgeBgHoverColor: var(--bg-filter-badge-accent);
$badgeColor: var(--fg-filter-badge);
$badgeBorderColor: var(--fg-filter-badge-accent);
$badgeBorderActiveColor: var(--fg-filter-badge);
.badge {
  display: flex;
  align-items: center;
  gap: $base-space * 1.3;
  max-width: 220px;
  margin: 0;
  padding: 2px $base-space;
  border: 1px solid $badgeBorderColor;
  border-radius: $border-radius-rounded;
  background-color: $badgeBgColor;
  color: $badgeColor;
  font-weight: 500;
  @include font-size(12px);
  @include line-height(16px);
  &--clickable {
    @extend .badge;
    &:not(.badge--active):hover {
      background-color: $badgeBgHoverColor;
    }
  }
  &--active {
    @extend .badge;
    background-color: $badgeBgHoverColor;
    border: 1px solid hsla(from $badgeBorderActiveColor h s l / 40%);
  }
  &__text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  &__close-button {
    padding: 0;
    flex-shrink: 0;
    border-radius: 0;
    &__icon {
      min-width: 10px;
      color: $badgeColor;
      &:hover {
        color: $badgeColor;
      }
    }
  }
}
</style>
