<template>
  <BaseTopbarBrand>
    <BaseBreadcrumbs
      v-if="breadcrumbs.length"
      :breadcrumbs="breadcrumbs"
      :copy-button="showCopyButton"
      @breadcrumb-action="$emit('breadcrumb-action', $event)"
    />
    <template v-if="datasetId && showSettingButton">
      <DatasetSettingsIconFeedbackTask @click="goToSetting(datasetId)" />
    </template>
    <div class="topbar--left">
      <slot name="badge"></slot>
    </div>
    <div class="topbar--right">
      <div class="topbar__buttons">
        <slot name="topbar-buttons" />
      </div>

      <user-avatar-tooltip />
    </div>
  </BaseTopbarBrand>
</template>

<script>
import { useRoutes } from "~/v1/infrastructure/services";

export default {
  name: "HeaderFeedbackTask",
  props: {
    datasetId: {
      type: String,
    },
    breadcrumbs: {
      type: Array,
      default: () => [],
    },
    showSettingButton: {
      type: Boolean,
      default: false,
    },
    showCopyButton: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    return useRoutes();
  },
};
</script>

<style lang="scss" scoped>
.topbar {
  &__buttons {
    display: flex;
    align-items: center;
    gap: $base-space * 2;
  }
  &--right {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: $base-space * 4;
    margin-left: auto;
    @include media("<=tablet") {
      gap: $base-space;
    }
  }
  &--left {
    margin-right: auto;
  }
}
</style>
