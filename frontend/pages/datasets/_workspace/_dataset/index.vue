<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <base-loading v-if="$fetchState.pending" />
  <div
    :class="[
      'app',
      annotationEnabled ? '--annotation' : '',
      areMetricsVisible ? '--metrics' : '',
    ]"
    v-else
  >
    <app-header
      :dataset="dataset"
      :breadcrumbs="breadcrumbs"
      @search-records="searchRecords"
    >
      <task-sidebar v-if="dataset" :dataset="dataset" />
    </app-header>
    <error
      v-if="$fetchState.error"
      link="/datasets"
      :where="datasetName"
      :error="$fetchState.error"
    ></error>
    <task-search v-else :dataset="dataset" @search-records="searchRecords" />
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import { currentWorkspace } from "@/models/Workspace";
import { getDatasetModelPrimaryKey } from "../../../../models/Dataset";

export default {
  layout: "app",
  async fetch() {
    await this.fetchByName(this.datasetName);
  },
  computed: {
    ...mapGetters({
      findByName: "entities/datasets/findByName",
    }),
    breadcrumbs() {
      return [
        { link: { path: "/datasets" }, name: "Datasets" },
        {
          link: { path: `/datasets?workspace=${this.workspace}` },
          name: this.workspace,
        },
        {
          link: this.$route.fullPath,
          name: this.dataset ? this.dataset.name : undefined,
        },
      ];
    },
    dataset() {
      // This computed data makes that store updates could be shown here
      try {
        return this.findByName(this.datasetName);
      } catch {
        return null;
      }
    },
    datasetName() {
      return this.$route.params.dataset;
    },
    workspace() {
      return currentWorkspace(this.$route);
    },
    datasetPrimaryKey() {
      const paramsToGetDatasetPrimaryKey = {
        name: this.datasetName,
        owner: this.workspace,
      };

      return getDatasetModelPrimaryKey(paramsToGetDatasetPrimaryKey);
    },
    areMetricsVisible() {
      return this.dataset && this.dataset.viewSettings.visibleMetrics;
    },
    annotationEnabled() {
      return this.dataset && this.dataset.viewSettings.viewMode === "annotate";
    },
  },
  methods: {
    ...mapActions({
      fetchByName: "entities/datasets/fetchByName",
      search: "entities/datasets/search",
    }),
    async searchRecords(query) {
      await this.search({ dataset: this.dataset, ...query });
    },
  },
};
</script>

<style lang="scss" scoped></style>
