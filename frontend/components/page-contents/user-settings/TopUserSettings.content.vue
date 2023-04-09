<template>
  <div class="top-content">
    <h1 v-text="title" />
    <BaseButton :to="goToDatasetsPage" class="secondary text">
      <svgicon name="chevron-left" width="10" height="10" color="#4C4EA3" />
      {{ nameOfDatasetsPage }}
    </BaseButton>
  </div>
</template>

<script>
export default {
  name: "TopUserSettingsContent",
  created() {
    this.nameOfDatasetsPage = "Home";
    this.title = "My settings";
    this.goToDatasetsPage = { name: "datasets" };
  },
};
</script>

<style lang="scss" scoped>
.top-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  border-bottom: 1px solid #e6e6e6;
}
</style>
