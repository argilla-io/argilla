<template>
  <BaseTopbarBrand>
    <BaseBreadcrumbs
      v-if="breadcrumbs.length"
      :breadcrumbs="breadcrumbs"
      :copy-button="showCopyButton"
      @breadcrumb-action="$emit('breadcrumb-action', $event)"
    />
    <template v-if="datasetId">
      <NuxtLink
        v-if="showSettingButton"
        :to="{ name: 'dataset-id-settings', params: { id: this.datasetId } }"
      >
        <DatasetSettingsIconFeedbackTask v-if="datasetId" />
      </NuxtLink>
    </template>
    <user-avatar-tooltip />
  </BaseTopbarBrand>
</template>

<script>
import { useRole } from "~/v1/infrastructure/services";

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
    return useRole();
  },
};
</script>
