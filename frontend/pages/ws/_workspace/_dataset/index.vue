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
  <re-loading v-if="$fetchState.pending" />
  <div
    :class="[
      'app',
      annotationEnabled ? '--annotation' : '',
      areMetricsVisible ? '--metrics' : '',
    ]"
    v-else
  >
    <app-header :dataset="dataset" :breadcrumbs="breadcrumbs">
      <task-sidebar v-if="dataset" :dataset="dataset" />
    </app-header>
    <error
      v-if="$fetchState.error"
      :link="errorLink"
      :where="datasetName"
      :error="$fetchState.error"
    ></error>
    <task-search v-else :dataset="dataset" />
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import { currentWorkspace, workspaceHome } from "@/models/Workspace";

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
        { link: { path: workspaceHome(this.workspace) }, name: this.workspace },
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
    errorLink() {
      return workspaceHome(this.workspace);
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
    }),
  },
};
</script>

<style lang="scss" scoped></style>
