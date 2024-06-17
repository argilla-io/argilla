<template>
  <div class="panel" :class="isExpanded ? '--expanded' : '--collapsed'">
    <BaseButton class="panel__header" @click="toggleExpand(isExpanded)">
      <slot name="panelHeader" />
      <svgicon
        class="panel__header__icon"
        :name="isExpanded ? 'chevron-down' : 'chevron-right'"
        width="12"
        height="12"
      />
    </BaseButton>

    <div class="panel__content" v-if="isExpanded">
      <slot name="panelContent" />
    </div>
  </div>
</template>

<script>
import "assets/icons/chevron-right";
import "assets/icons/chevron-down";
export default {
  props: {
    isExpanded: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    toggleExpand(value) {
      this.$emit("toggle-expand", !value);
    },
  },
};
</script>
<style lang="scss" scoped>
.panel {
  flex: 1;
  align-items: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-top: 1px solid $black-10;

  &__header {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $base-space $base-space * 2;
    @include font-size(13px);
    :deep(p) {
      text-transform: uppercase;
    }
    &__icon {
      padding: 0;
      flex-shrink: 0;
    }
    &:hover {
      :deep(p),
      :deep(svg) {
        color: darken(palette(grey, 300), 10%);
      }
    }
  }

  &__content {
    width: 100%;
    height: 100%;
    padding: $base-space $base-space * 2;
    overflow-y: auto;
    @include font-size(13px);
  }
}
</style>
