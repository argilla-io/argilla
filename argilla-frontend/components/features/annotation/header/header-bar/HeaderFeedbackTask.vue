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
    <user-avatar-tooltip />
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
