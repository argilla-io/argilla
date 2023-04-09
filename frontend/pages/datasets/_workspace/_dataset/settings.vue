<template>
  <HeaderAndTopAndTwoColumns>
    <template v-slot:header>
      <HeaderComponent />
    </template>
    <template v-slot:top>
      <TopDatasetSettingsContent />
    </template>
    <template v-slot:left>
      <LeftDatasetSettingsContent />
    </template>
    <template v-slot:right>
      <div class="right-content"></div>
    </template>
  </HeaderAndTopAndTwoColumns>
</template>

<script>
import HeaderAndTopAndTwoColumns from "@/layouts/HeaderAndTopAndTwoColumns";

export default {
  name: "SettingsPage",
  components: {
    HeaderAndTopAndTwoColumns,
  },
};
</script>
