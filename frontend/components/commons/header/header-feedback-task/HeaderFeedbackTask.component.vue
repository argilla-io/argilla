<template>
  <BaseTopbarBrand>
    <BaseBreadcrumbs
      v-if="breadcrumbs.length"
      :breadcrumbs="breadcrumbs"
      :copy-button="showCopyButton"
      @breadcrumb-action="$emit('breadcrumb-action', $event)"
    />
    <template v-if="datasetId">
      <BaseButton
        ref="trainButtonRef"
        class="header__button small"
        @on-click="onClickTrain"
        v-if="isAdminOrOwnerRole && showTrainButton"
      >
        <svgicon name="code" width="20" height="20" />Train
      </BaseButton>
      <NuxtLink
        v-if="showSettingButton"
        :to="{ name: 'dataset-id-settings', params: { id: this.datasetId } }"
      >
        <DatasetSettingsIconFeedbackTaskComponent v-if="datasetId" />
      </NuxtLink>
    </template>
    <user-avatar-tooltip />
  </BaseTopbarBrand>
</template>

<script>
import { useRole } from "~/v1/infrastructure/services";

export default {
  name: "HeaderFeedbackTaskComponent",
  props: {
    datasetId: {
      type: String,
    },
    breadcrumbs: {
      type: Array,
      default: () => [],
    },
    showTrainButton: {
      type: Boolean,
      default: false,
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
  methods: {
    onClickTrain() {
      this.$emit("on-click-train");
    },
  },
  setup() {
    return useRole();
  },
};
</script>

<style lang="scss" scoped>
$header-button-color: #262a2e;
.header__button {
  background: $header-button-color;
  color: palette(white);
  margin-right: $base-space;
  padding: 10px 12px 10px 10px;
  font-weight: 600;
  @include font-size(14px);
  box-shadow: $shadow-200;
  &:hover {
    background: lighten($header-button-color, 3%);
  }
  svg {
    fill: palette(white);
  }
}
</style>
