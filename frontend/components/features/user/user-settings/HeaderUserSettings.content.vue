<template>
  <BaseTopbarBrand v-once>
    <BaseBreadcrumbs
      v-if="breadcrumbs"
      :breadcrumbs="breadcrumbs"
      @breadcrumb-action="$emit('breadcrumb-action', $event)"
    />
    <user-avatar-tooltip />
  </BaseTopbarBrand>
</template>

<script>
import { ROUTES } from "@/v1/infrastructure/services";
export default {
  name: "HeaderUserSettingsComponent",
  created() {
    this.breadcrumbs = [
      { link: { name: ROUTES.datasets }, name: "Home" },
      {
        link: {},
        name: "my settings",
      },
    ];
  },
};
</script>
