<template>
  <BaseLoading v-if="isLoadingDataset" />
  <div v-else>
    <HeaderFeedbackTaskComponent
      :datasetId="datasetId"
      :breadcrumbs="breadcrumbs"
    />
    <div class="settings__content">
      <TopDatasetSettingsFeedbackTaskContent
        :datasetId="datasetId"
        class="settings__header"
      />
      <BaseTabs
        :tabs="settingTabs"
        :active-tab="visibleTab"
        @change-tab="getSelectedTab"
        class="settings__tabs"
      />
      <transition name="fade" mode="out-in" appear>
        <component
          :is="visibleComponent"
          :key="visibleComponent"
          :settings="datasetSetting"
        />
      </transition>
    </div>
  </div>
</template>

<script>
import HeaderAndTopAndTwoColumns from "@/layouts/HeaderAndTopAndTwoColumns";
import { useDatasetSettingViewModel } from "./useDatasetSettingViewModel";

export default {
  name: "SettingsPage",
  components: {
    HeaderAndTopAndTwoColumns,
  },
  data() {
    return {
      settingTabs: [
        { id: "info", name: "Info", component: "settingsInfo" },
        { id: "fields", name: "Fields", component: "settingsFields" },
        { id: "questions", name: "Questions", component: "settingsQuestions" },
        {
          id: "danger-zone",
          name: "Danger zone",
          component: "settingsDangerZone",
        },
      ],
      selectedComponent: null,
    };
  },
  computed: {
    visibleTab() {
      return this.selectedComponent || this.settingTabs[0];
    },
    visibleComponent() {
      return this.visibleTab.component;
    },
  },
  methods: {
    getSelectedTab(id) {
      this.selectedComponent = this.settingTabs.find((tab) => tab.id === id);
    },
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
    margin: 0 auto;
    padding: 0 4em;
    height: calc(100vh - $topbarHeight);
  }
  &__header.top-content {
    height: auto;
    padding: 2em 0;
  }
  &__tabs {
    & ~ #{$this}__header {
      border: 1px solid red;
    }
  }
}
</styles>
