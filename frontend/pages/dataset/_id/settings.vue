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
        <BaseTabsAndContent :tabs="tabs" class="settings__tabs-content">
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
  $this: &;
  &__content {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  &__header.top-content {
    padding-top: 2em;
    border-bottom: none;
    flex: 1;
    &.--separator {
      border-bottom: 1px solid $black-10;
      padding-bottom: 2em;
    }
  }

  &__tabs {
    &-content {
      height: calc(100% - $topbarHeight);
    }
  }
}
</styles>
