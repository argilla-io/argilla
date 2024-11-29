<template>
  <TransitionGroup
    v-if="datasets.length"
    name="list"
    tag="ul"
    class="dataset-list__cards"
  >
    <li v-for="dataset in datasets" :key="dataset.id" :id="dataset.id">
      <DatasetCard v-if="hydrate[dataset.id]" :dataset="dataset" />
    </li>
  </TransitionGroup>

  <p
    v-else
    class="dataset-list__empty-message --heading3"
    v-text="$t('home.zeroDatasetsFound')"
  />
</template>

<script>
export default {
  data() {
    return {
      hydrate: {},
    };
  },
  props: {
    datasets: {
      type: Array,
      required: true,
    },
  },
  watch: {
    datasets() {
      this.hydrateDatasetList();
    },
  },
  methods: {
    hydrateDatasetList() {
      const handleIntersection = (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            this.$set(this.hydrate, entry.target.id, true);
          }
        }
      };

      const observer = new IntersectionObserver(handleIntersection);

      this.datasets.forEach((item) => {
        this.$nextTick(() => {
          const element = document.getElementById(item.id);
          if (!element) return;

          observer.observe(element);
        });
      });
    },
  },
  mounted() {
    this.hydrateDatasetList();
  },
};
</script>

<style lang="scss" scoped>
.dataset-list {
  &__cards {
    display: grid;
    gap: $base-space * 2;
    grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
    grid-auto-rows: 1fr;
    list-style: none;
    padding: 0;
    margin-bottom: $base-space * 4;

    li {
      min-height: 260px;
    }
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
