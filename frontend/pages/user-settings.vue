<template>
  <HeaderAndTopAndTwoColumns>
    <template v-slot:header>
      <HeaderFeedbackTaskComponent
        :breadcrumbs="[
          { link: { name: 'datasets' }, name: 'Home' },
          { link: {}, name: 'my settings' },
        ]"
      />
    </template>
    <template v-slot:top>
      <TopUserSettingsContent />
    </template>
    <template v-slot:left>
      <LeftUserSettingsContent />
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
