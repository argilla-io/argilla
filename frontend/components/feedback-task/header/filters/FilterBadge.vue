<template>
  <component
    :class="[
      clickable ? 'badge--clickable' : 'badge',
      activeBadge ? 'badge--active' : 'badge',
    ]"
    :is="renderComponent"
    @click="onClick($event)"
    >{{ text }}
    <BaseButton
      v-if="clearable"
      class="badge__close-button"
      @click="onClear($event)"
    >
      <svgicon
        class="badge__close-button__icon"
        name="close"
        width="12"
        height="12"
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
$badgeBgColor: palette(purple, 300);
$badgeBgHoverColor: palette(purple, 400);
$badgeColor: palette(purple, 200);
$badgeBorderColor: #b6b9ff;
$badgeBorderActiveColor: palette(purple, 200);
.badge {
  display: flex;
  align-items: center;
  gap: $base-space * 1.3;
  min-width: 0;
  margin: 0;
  padding: calc($base-space / 2) $base-space;
  border: 1px solid $badgeBorderColor;
  border-radius: $border-radius-rounded;
  background-color: $badgeBgColor;
  color: $badgeColor;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  @include font-size(12px);
  @include line-height(12px);
  &--clickable {
    @extend .badge;
    &:not(.badge--active):hover {
      background-color: darken($badgeBgColor, 2%);
    }
  }
  &--active {
    @extend .badge;
    background-color: darken($badgeBgColor, 5%);
    border: 1px solid $badgeBorderActiveColor;
  }
  &__close-button {
    padding: 0;
    flex-shrink: 0;
    border-radius: 0;
    &__icon {
      min-width: 12px;
      color: $badgeColor;
      &:hover {
        color: darken($badgeColor, 90%);
      }
    }
  }
}
</style>
