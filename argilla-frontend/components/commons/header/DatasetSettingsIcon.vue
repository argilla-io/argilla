<template>
  <BaseIconWithBadge
    class="button-settings"
    tooltip="Dataset settings"
    :show-badge="showBadge"
    badge-vertical-position="top"
    badge-horizontal-position="right"
    badge-border-color="#212121"
    icon="settings"
    @click-icon="onClickSettingsIcon"
  />
</template>

<script>
import {
  isExistAnyLabelsNotSavedInBackByDatasetId,
  getTotalLabelsInGlobalLabel,
} from "@/models/globalLabel.queries";
import { getDatasetTaskById } from "@/models/dataset.utilities";

export default {
  props: {
    datasetId: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      isLoading: false,
    };
  },
  computed: {
    datasetTask() {
      return getDatasetTaskById(this.datasetId);
    },
    isTaskTokenClassification() {
      return this.datasetTask === "TokenClassification";
    },
    isTaskTextClassification() {
      return this.datasetTask === "TextClassification";
    },
    isNoLabelInGlobalLabelModel() {
      return !getTotalLabelsInGlobalLabel(this.datasetId);
    },
    isAnyLabelsInGlobalLabelsModelNotSavedInBack() {
      return isExistAnyLabelsNotSavedInBackByDatasetId(this.datasetId);
    },
    showBadge() {
      if (this.isLoading) {
        return false;
      }
      return (
        (this.isNoLabelInGlobalLabelModel ||
          this.isAnyLabelsInGlobalLabelsModelNotSavedInBack) &&
        (this.isTaskTokenClassification || this.isTaskTextClassification)
      );
    },
  },
  mounted() {
    this.onBusEventIsLoadingLabels();
  },
  methods: {
    onClickSettingsIcon() {
      this.$emit("click-settings-icon");
    },
    onBusEventIsLoadingLabels() {
      this.$root.$on("is-loading-value", (loadingState) => {
        this.isLoading = loadingState;
      });
    },
  },
  destroyed() {
    this.$root.$off("is-loading-value");
  },
};
</script>
<style lang="scss" scoped>
.button-settings {
  margin-right: $base-space;
  &[data-title] {
    position: relative;
    overflow: visible;
    @extend %has-tooltip--bottom;
    &:before,
    &:after {
      margin-top: calc($base-space/2);
    }
  }
}
</style>
