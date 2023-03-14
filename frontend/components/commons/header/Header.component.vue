<template>
  <BaseTopbarBrand>
    <BaseBreadcrumbs
      v-if="breadcrumbs"
      :breadcrumbs="breadcrumbs"
      :copy-button="copyButton"
      @breadcrumb-action="$emit('breadcrumb-action', $event)"
    />
    <user />
  </BaseTopbarBrand>
</template>

<script>
export default {
  name: "HeaderComponent",
  data() {
    return {
      copyButton: false,
    };
  },
  computed: {
    workspace() {
      return this.$route.params.workspace;
    },
    datasetName() {
      return this.$route.params.dataset;
    },
    datasetLinkPage() {
      return this.$route.fullPath.replace("/settings", "");
    },
    datasetSettingsPage() {
      return this.$route.fullPath;
    },
    breadcrumbs() {
      return [
        { link: { path: "/datasets" }, name: "Datasets" },
        {
          link: { path: `/datasets?workspace=${this.workspace}` },
          name: this.workspace,
        },
        {
          link: this.datasetLinkPage,
          name: this.datasetName,
        },
        {
          link: null,
          name: "settings",
        },
      ];
    },
  },
};
</script>

<style lang="scss" scoped></style>
