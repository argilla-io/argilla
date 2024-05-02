<template>
  <InternalPage>
    <template v-slot:header>
      <HeaderComponent />
    </template>
    <template v-slot:content>
      <div>
        <TopDatasetSettingsContent />
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
