<template>
  <HeaderAndTopAndTwoColumns>
    <template v-slot:header>
      <HeaderUserSettingsContent />
    </template>
    <template v-slot:top></template>
    <template v-slot:left></template>
    <template v-slot:right>
      <div class="right-content"></div>
    </template>
  </HeaderAndTopAndTwoColumns>
</template>

<script>
import HeaderAndTopAndTwoColumns from "@/layouts/HeaderAndTopAndTwoColumns";

export default {
  name: "UserSettingsPage",
  components: {
    HeaderAndTopAndTwoColumns,
  },
};
</script>
