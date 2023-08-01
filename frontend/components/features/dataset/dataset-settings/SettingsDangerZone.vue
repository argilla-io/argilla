<template>
  <div>
    <h1>Danger zone</h1>
    <DatasetDeleteFeedbackTaskComponent :dataset="settings.dataset" />
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
