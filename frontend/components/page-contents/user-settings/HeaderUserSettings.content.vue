<template>
  <div>
    <BaseTopbarBrand>
      <BaseBreadcrumbs
        v-if="breadcrumbs"
        :breadcrumbs="breadcrumbs"
        @breadcrumb-action="$emit('breadcrumb-action', $event)"
      />
      <user />
    </BaseTopbarBrand>
  </div>
</template>

<script>
export default {
  name: "HeaderUserSettingsComponent",
  computed: {
    breadcrumbs() {
      return [
        { link: { name: "datasets" }, name: "Home" },
        {
          link: null,
          name: "my settings",
        },
      ];
    },
  },
};
</script>
