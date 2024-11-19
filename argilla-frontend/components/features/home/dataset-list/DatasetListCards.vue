<template>
  <TransitionGroup
    v-if="datasets.length"
    name="list"
    tag="ul"
    class="dataset-list__cards"
  >
    <li v-for="dataset in datasets" :key="dataset.id">
      <NuxtLink :to="getDatasetLink(dataset)" class="dataset-list__link">
        <DatasetCard
          @go-to-settings="goToSetting(dataset.id)"
          @copy-url="copyUrl(dataset)"
          @copy-name="copyName(dataset.name)"
          :dataset="dataset"
        />
      </NuxtLink>
    </li>
  </TransitionGroup>

  <p
    class="dataset-list__empty-message --heading3"
    v-else
    v-text="$t('home.zeroDatasetsFound')"
  />
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
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    grid-auto-rows: auto;
    list-style: none;
    padding: 0;
    margin-bottom: $base-space * 4;
  }
  &__link {
    text-decoration: none;
  }
  &__empty-message {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 50vh;
    color: var(--fg-tertiary);
  }
}
.list-move,
.list-enter-active,
.list-leave-active {
  transition: transform 0.2s ease-in, opacity 0.1s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(10px);
}
.list-leave-active {
  position: absolute;
}
</style>
