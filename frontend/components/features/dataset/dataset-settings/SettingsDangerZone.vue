<template>
  <div>
    <h1>Delete dataset</h1>
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
