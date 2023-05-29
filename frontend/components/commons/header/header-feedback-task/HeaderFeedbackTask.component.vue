<template>
  <BaseTopbarBrand>
    <BaseBreadcrumbs
      v-if="breadcrumbs.length"
      :breadcrumbs="breadcrumbs"
      :copy-button="copyButton"
      @breadcrumb-action="$emit('breadcrumb-action', $event)"
    />
    <NuxtLink
      :to="{ name: 'dataset-id-settings', params: { id: this.datasetId } }"
    >
      <DatasetSettingsIconFeedbackTaskComponent
        v-if="datasetId"
        :datasetId="datasetId"
      />
    </NuxtLink>
    <user />
  </BaseTopbarBrand>
</template>

<script>
export default {
  name: "HeaderFeedbaskTaskComponent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
    breadcrumbs: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      copyButton: false,
    };
  },
};
</script>
