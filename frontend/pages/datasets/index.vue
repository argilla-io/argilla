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
  <div class="home">
    <base-loading v-if="isLoadingDatasets" />
    <div v-else>
      <div class="home__main">
        <app-header
          :copy-button="false"
          :sticky="false"
          :breadcrumbs="[{ action: 'clearFilters', name: 'Home' }]"
          @breadcrumb-action="onBreadcrumbAction($event)"
        />
        <error
          v-if="$fetchState.error"
          where="workspace datasets"
          :error="$fetchState.error"
        />
        <datasets-table v-else ref="table" :datasets="datasets.datasets" />
      </div>
      <sidebar-menu
        class="home__sidebar"
        @refresh="$fetch"
        :sidebar-items="[
          {
            id: 'refresh',
            tooltip: 'Refresh',
            icon: 'refresh',
            group: 'Refresh',
            action: 'refresh',
          },
        ]"
      />
    </div>
  </div>
</template>

<script>
import { useDatasetsViewModel } from "./useDatasetsViewModel";

export default {
  layout: "app",
  methods: {
    onBreadcrumbAction(e) {
      if (e === "clearFilters") {
        this.$refs.table?.clearFilters();
      }
    },
  },
  setup() {
    return useDatasetsViewModel();
  },
};
</script>

<style lang="scss" scoped>
.home {
  &__main {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }

  &__sidebar.sidebar {
    position: fixed;
    top: 56px;
    right: 0;
    border-left: 1px solid palette(grey, 600);
  }
}
</style>
