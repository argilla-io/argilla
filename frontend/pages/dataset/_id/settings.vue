<template>
  <BaseLoading v-if="isLoadingDataset" />
  <InternalPage v-else>
    <template v-slot:header>
      <HeaderFeedbackTaskComponent
        :datasetId="datasetId"
        :breadcrumbs="breadcrumbs"
      />
    </template>
    <template v-slot:container>
      <div class="settings__wrapper">
        <TopDatasetSettingsFeedbackTaskContent
          class="settings__header"
          :separator="!isAdminOrOwnerRole"
          @goToDataset="goToDataset"
        />
        <SettingsInfoReadOnly
          v-if="!isAdminOrOwnerRole"
          :settings="datasetSetting"
        />
        <BaseTabsAndContent
          v-else
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
  </InternalPage>
</template>

<script>
import InternalPage from "@/layouts/InternalPage";
import { useDatasetSettingViewModel } from "./useDatasetSettingViewModel";

export default {
  name: "SettingPage",
  components: {
    InternalPage,
  },
  setup() {
    return useDatasetSettingViewModel();
  },
};
</script>

<styles lang="scss" scoped>
.settings {
  &__wrapper {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  &__tabs {
    &-content {
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 0;
      .tabs {
        flex-wrap: wrap;
      }
    }
  }
}
</styles>
