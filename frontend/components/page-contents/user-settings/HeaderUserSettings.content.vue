<template>
  <BaseTopbarBrand v-once>
    <BaseBreadcrumbs
      v-if="breadcrumbs"
      :breadcrumbs="breadcrumbs"
      @breadcrumb-action="$emit('breadcrumb-action', $event)"
    />
    <user />
  </BaseTopbarBrand>
</template>

<script>
export default {
  name: "HeaderUserSettingsComponent",
  created() {
    this.breadcrumbs = [
      { link: { name: "datasets" }, name: "Home" },
      {
        link: null,
        name: "my settings",
      },
    ];
  },
};
</script>
