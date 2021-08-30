<template>
  <re-loading v-if="$fetchState.pending" />
  <error
    v-else-if="$fetchState.error"
    link="/"
    :where="datasetName"
    :error="$fetchState.error"
  ></error>
  <task-search v-else :dataset="dataset" />
</template>

<script>
import { mapActions, mapGetters } from "vuex";
export default {
  layout: "app",
  async fetch() {
    await this.loadByName(this.datasetName);
  },
  computed: {
    ...mapGetters({
      getByName: "entities/datasets/byName",
    }),

    dataset() {
      // This computed data makes that store updates could be shown here
      return this.getByName(this.datasetName);
    },
    datasetName() {
      return this.$route.params.id;
    },
  },
  methods: {
    ...mapActions({
      loadByName: "entities/datasets/fetchByName",
    }),
  },
};
</script>
