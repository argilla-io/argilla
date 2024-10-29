<template>
  <div
    class="panel"
    :class="[
    !isExpanded ? '--collapsed' : undefined,
    hideOnDesktop ? '--mobile' : undefined,
  ]"
  >
    <BaseButton
      class="panel__header"
      @click="toggleExpand(isExpanded)"
      :aria-expanded="isExpanded ? 'true' : 'false'"
      :aria-label="isExpanded ? 'Collapse Panel' : 'Expand Panel'"
    >
      <div class="panel__header__container">
        <slot v-if="!isExpanded" name="panelHeader" />
        <div v-else style="width: 100%; text-align: left">
          <slot name="panelHeaderExpanded" />
        </div>
        <svgicon
          class="panel__header__icon"
          :name="isExpanded ? 'chevron-down' : 'chevron-right'"
          width="12"
          height="12"
          aria-hidden="true"
        />
      </div>
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
    hideOnDesktop: {
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
  border-top: 1px solid var(--bg-opacity-10);

  &__header {
    overflow: visible;
    color: var(--fg-secondary);

    &__container {
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;

      @include media("<desktop") {
        height: $base-space * 3;
      }
    }

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
        color: var(--fg-primary);
        opacity: 0.7;
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

.--collapsed {
  @include media("<desktop") {
    max-height: 6vh;
  }
}

.--mobile {
  @include media(">=desktop") {
    display: none !important;
  }
}
</style>
