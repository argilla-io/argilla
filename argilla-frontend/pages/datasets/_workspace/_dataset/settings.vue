<template>
  <InternalPage>
    <template v-slot:header>
      <HeaderComponent />
    </template>
    <template v-slot:page-header>
      <TopDatasetSettingsContent />
    </template>
    <template v-slot:page-content>
      <div>
        <LeftDatasetSettingsContent />
      </div>
    </template>
  </InternalPage>
</template>

<script>
import InternalPage from "@/layouts/InternalPage";

export default {
  name: "SettingsPage",
  components: {
    InternalPage,
  },
};
</script>
