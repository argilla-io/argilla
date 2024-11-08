<template>
  <ul v-if="datasets.length" class="dataset-list__cards">
    <li v-for="dataset in datasets" :key="dataset.id">
      <NuxtLink :to="getDatasetLink(dataset)">
        <DatasetCard
          @go-to-settings="goToSetting"
          @copy-url="copyUrl(dataset)"
          @copy-name="copyName(dataset.name)"
          :dataset="dataset"
        />
      </NuxtLink>
    </li>
  </ul>
  <p v-else>
    {{ $t("home.zeroDatasetsFound") }}
  </p>
</template>

<script>
import { useRoutes } from "@/v1/infrastructure/services";

export default {
  props: {
    datasets: {
      type: Array,
      required: true,
    },
  },
  methods: {
    copyUrl(dataset) {
      this.copy(`${window.origin}${this.getDatasetLink(dataset)}`);
    },
    copyName(name) {
      this.copy(name);
    },
    copy(value) {
      this.$copyToClipboard(value);
    },
  },
  setup() {
    return useRoutes();
  },
};
</script>

<style lang="scss" scoped>
.dataset-list {
  &__cards {
    display: grid;
    gap: $base-space * 2;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    grid-auto-rows: 1fr;
    list-style: none;
    padding: 0;
  }
}
</style>
