<template>
  <div class="settings__container">
    <div class="settings__content">
      <h2 class="--heading5 --medium">Delete dataset</h2>
      <DatasetDeleteFeedbackTask :dataset="settings.dataset" />
    </div>
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
    display: flex;
    gap: $base-space * 4;
    height: 100%;
    flex-wrap: wrap;
    min-height: 0;
    padding-top: $base-space;
    overflow: auto;
  }

  &__content {
    flex: 1;
    max-width: 1000px;
  }
}
</style>
