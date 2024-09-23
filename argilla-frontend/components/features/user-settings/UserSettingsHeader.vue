<template>
  <div class="user-settings__header">
    <h1 v-text="$t('userSettings.title')" />
    <BaseButton :to="datasetsURL" class="secondary text">
      <svgicon
        name="chevron-left"
        width="10"
        height="10"
        color="var(--bg-secondary)"
      />
      {{ $t("breadcrumbs.home") }}
    </BaseButton>
  </div>
</template>

<script>
import { ROUTES } from "@/v1/infrastructure/services";

export default {
  name: "TopUserSettingsContent",
  created() {
    this.datasetsURL = ROUTES.datasets;
  },
};
</script>

<style lang="scss" scoped>
.user-settings__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--bg-opacity-20);
  @include media(">tablet") {
    min-height: 100px;
  }
}
</style>
