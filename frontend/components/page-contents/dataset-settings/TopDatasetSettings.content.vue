<template>
  <div class="top-content">
    <h1 v-html="title" />
    <NuxtLink :to="datasetPageUrl">
      {{ goToDatasetPageLabel }}
    </NuxtLink>
  </div>
</template>

<script>
export default {
  name: "TopDatasetSettingsContent",
  data() {
    return {
      title: "Dataset settings",
      goToDatasetPageLabel: "< See your dataset",
    };
  },
  computed: {
    datasetPageUrl() {
      const { fullPath } = this.$route;
      const datasetPageUrl = fullPath.replace("/settings?", "?");
      return datasetPageUrl;
    },
  },
};
</script>

<style lang="scss" scoped>
.top-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}
</style>
