<template>
  <BaseTopbarBrand>
    <BaseBreadcrumbs
      v-if="breadcrumbs"
      :breadcrumbs="breadcrumbs"
      :copy-button="copyButton"
      @breadcrumb-action="$emit('breadcrumb-action', $event)"
    />
    <DatasetSettingsIcon
      v-if="datasetName"
      :visible-badge="
        isNoLabelInGlobalLabelModel ||
        isAnyLabelsInGlobalLabelsModelNotSavedInBack
      "
      @click-settings-icon="goToSettings()"
    />
    <user />
  </BaseTopbarBrand>
</template>

<script>
import { getDatasetModelPrimaryKey } from "@/models/Dataset";
import {
  isExistAnyLabelsNotSavedInBackByDatasetId,
  getTotalLabelsInGlobalLabel,
} from "@/models/globalLabel.queries";
export default {
  name: "HeaderComponent",
  data() {
    return {
      copyButton: false,
    };
  },
  computed: {
    datasetId() {
      return getDatasetModelPrimaryKey({
        name: this.datasetName,
        workspace: this.workspace,
      });
    },
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
    isNoLabelInGlobalLabelModel() {
      return !getTotalLabelsInGlobalLabel(this.datasetId);
    },
    isAnyLabelsInGlobalLabelsModelNotSavedInBack() {
      return isExistAnyLabelsNotSavedInBackByDatasetId(this.datasetId);
    },
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

<style lang="scss" scoped></style>
