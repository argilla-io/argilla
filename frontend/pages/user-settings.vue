<template>
  <InternalPage>
    <template v-slot:header>
      <HeaderFeedbackTaskComponent
        :breadcrumbs="[
          { link: { name: 'datasets' }, name: $t('breadcrumbs.home') },
          { link: {}, name: $t('breadcrumbs.userSettings') },
        ]"
      />
    </template>
    <template v-slot:content>
      <div class="settings__wrapper">
        <UserSettingsHeader />
        <UserSettingsContent />
      </div>
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

<styles lang="scss" scoped>
.settings {
  &__wrapper {
    display: flex;
    flex-direction: column;
    height: auto;
  }
}
</styles>
