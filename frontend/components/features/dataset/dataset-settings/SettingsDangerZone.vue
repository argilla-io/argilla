<template>
  <div class="settings__container">
    <h2 class="--heading5 --medium">Delete dataset</h2>
    <DatasetDeleteFeedbackTask :dataset="settings.dataset" />
  </div>
</template>

<script>
export default {
  name: "SettingsDangerZone",
  props: {
    settings: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.settings {
  &__container {
    max-width: 1000px;
  }
}
</style>
