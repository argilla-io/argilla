<template>
  <BaseTopbarBrand>
    <BaseBreadcrumbs
      v-if="breadcrumbs.length"
      :breadcrumbs="breadcrumbs"
      :copy-button="showCopyButton"
      @breadcrumb-action="$emit('breadcrumb-action', $event)"
    />
    <template v-if="datasetId && showSettingButton">
      <div @click="goToSetting(datasetId)">
        <DatasetSettingsIconFeedbackTask />
      </div>
    </template>
    <div class="topbar--right">
      <slot name="dialog-cta"></slot>
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
.topbar--right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: $base-space * 4;
  margin-left: auto;
  @include media("<=tablet") {
    gap: $base-space;
  }
}
</style>
