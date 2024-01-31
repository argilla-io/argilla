<template>
  <div class="top-content">
    <h1 v-text="$t('userSettings.title')" />
    <BaseButton :to="datasetsURL" class="secondary text">
      <svgicon name="chevron-left" width="10" height="10" color="#4C4EA3" />
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
.top-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  border-bottom: 1px solid #e6e6e6;
}
</style>
