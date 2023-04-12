<template>
  <BaseTopbarBrand>
    <BaseBreadcrumbs
      v-if="breadcrumbs.length"
      :breadcrumbs="breadcrumbs"
      :copy-button="copyButton"
      @breadcrumb-action="$emit('breadcrumb-action', $event)"
    />
    <DatasetSettingsIcon
      v-if="workspace && datasetName"
      :datasetId="[workspace, datasetName]"
      @click-settings-icon="goToSettings()"
    />
    <user />
  </BaseTopbarBrand>
</template>

<script>
export default {
  name: "HeaderFeedbaskTaskComponent",
  props: {
    datasetName: {
      type: String,
      required: true,
    },
    workspace: {
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
  methods: {
    goToSettings() {
      const currentRoute = this.$route.path;
      const newRoute = `/datasets/${this.workspace}/${this.datasetName}/settings`;
      const allowNavigate = currentRoute !== newRoute;
      if (this.datasetName && allowNavigate) {
        this.$router.push(newRoute);
      }
    },
  },
};
</script>
