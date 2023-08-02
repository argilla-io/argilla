<template>
  <BaseLoading v-if="isLoadingDataset" />
  <HeaderAndOneColumn v-else>
    <template v-slot:header>
      <HeaderFeedbackTaskComponent
        :datasetId="datasetId"
        :breadcrumbs="breadcrumbs"
      />
    </template>
    <template v-slot:center>
      <div class="settings__content">
        <TopDatasetSettingsFeedbackTaskContent
          :datasetId="datasetId"
          class="settings__header"
          :class="{ '--separator': !isAdminOrOwnerRole }"
        />
        <BaseTabsAndContent
          :tabs="tabs"
          tab-size="large"
          class="settings__tabs-content"
        >
          <template v-slot="{ currentComponent }">
            <component
              :is="currentComponent"
              :key="currentComponent"
              :settings="datasetSetting"
            />
          </template>
        </BaseTabsAndContent>
      </div>
    </template>
  </HeaderAndOneColumn>
</template>

<script>
import HeaderAndOneColumn from "@/layouts/HeaderAndOneColumn";
import { useDatasetSettingViewModel } from "./useDatasetSettingViewModel";

export default {
  name: "SettingPage",
  components: {
    HeaderAndOneColumn,
  },
  setup() {
    return useDatasetSettingViewModel();
  },
};
</script>

<styles lang="scss" scoped>
.settings {
  &__content {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding-bottom: $base-space;
  }
  &__header.top-content {
    padding-top: 2em;
    border-bottom: none;
    height: auto;
    &.--separator {
      border-bottom: 1px solid $black-10;
      padding-bottom: 2em;
    }
  }
  &__tabs {
    &-content {
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 0;
    }
  }
}
</styles>
