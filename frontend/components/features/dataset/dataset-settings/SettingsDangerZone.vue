<template>
  <div class="dataset-settings__danger-zone">
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
.dataset-settings {
  &__danger-zone {
    max-width: 1000px;
  }
}
</style>
