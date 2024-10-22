<template>
  <InternalPage>
    <template v-slot:header>
      <HeaderFeedbackTask
        :breadcrumbs="[
          { link: { path: 'index' }, name: $t('breadcrumbs.home') },
          { link: {}, name: $t('breadcrumbs.userSettings') },
        ]"
      />
    </template>
    <template v-slot:page-header>
      <UserSettingsHeader />
    </template>
    <template v-slot:page-content>
      <UserSettingsContent />
    </template>
  </InternalPage>
</template>

<script>
import InternalPage from "@/layouts/InternalPage";

export default {
  name: "UserSettingsPage",
  components: {
    InternalPage,
  },
};
</script>
