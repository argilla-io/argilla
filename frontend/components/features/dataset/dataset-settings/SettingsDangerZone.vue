<template>
  <div>
    <h2 class="--heading5 --semibold">Delete dataset</h2>
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
