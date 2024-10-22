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
  <Home>
    <template v-slot:header>
      <AppHeader
        class="home__header"
        :breadcrumbs="[
          { action: 'clearFilters', name: $t('breadcrumbs.home') },
        ]"
        @breadcrumb-action="onBreadcrumbAction"
      />
      <PersistentStorageBanner class="home__banner" />
    </template>
    <template v-slot:page-content>
      <h1 class="home__title">Argilla datasets</h1>
      <BaseLoading class="home__title" v-if="isLoadingDatasets" />
      <DatasetsTable
        v-else
        class="home__table"
        ref="table"
        :datasets="datasets.datasets"
        @on-click-card="cardAction"
      />
    </template>
    <template v-slot:page-sidebar>
      <template v-if="isAdminOrOwnerRole">
        <div class="home__sidebar__buttons">
          <ImportFromHub
            :is-expanded="showImportDatasetInput"
            @on-expand="showImportDatasetInput = true"
            @on-close="showImportDatasetInput = false"
            @on-import-dataset="importDataset"
          />
          <ImportFromPython v-if="!showImportDatasetInput" />
        </div>
        <div class="home__sidebar__content">
          <p class="home__sidebar__title">Don’t know where to start?</p>
          <p class="home__sidebar__subtitle">Explore these example datasets</p>
          <div class="home__sidebar__cards">
            <ExampleDataset
              v-for="dataset in exampleDatasets"
              :key="dataset.repoId"
              :dataset="dataset"
              @on-import-dataset="importDataset"
            />
          </div>
        </div>
      </template>
    </template>
  </Home>
</template>

<script>
import Home from "@/layouts/Home";
import { useHomeViewModel } from "./useHomeViewModel";

export default {
  data() {
    return {
      showImportDatasetInput: false,
    };
  },
  methods: {
    onBreadcrumbAction(e) {
      if (e === "clearFilters") {
        this.$refs.table?.clearFilters();
      }
    },
    cardAction(action) {
      if (action === "expand-import-dataset") {
        this.showImportDatasetInput = true;
      }
    },
    importDataset(repoId) {
      this.getNewDatasetByRepoId(repoId);
    },
  },
  components: {
    Home,
  },
  setup() {
    return useHomeViewModel();
  },
};
</script>

<style lang="scss" scoped>
.home {
  &__title {
    margin: 0;
    @include font-size(20px);
    font-weight: 500;
  }
  &__main {
    display: flex;
    flex-direction: column;
    height: 100vh;
    @include media("<desktop") {
      max-height: 100svh;
    }
  }
  &__header {
    min-height: $topbarHeight;
  }
  &__banner {
    width: auto;
  }
  &__table {
    min-height: 0;
    height: 100%;
    overflow: auto;
    padding: 0;
  }
  &__sidebar {
    &__content {
      display: flex;
      flex-direction: column;
      gap: $base-space;
      overflow: auto;
    }
    &__buttons {
      display: flex;
      gap: $base-space;
      flex-wrap: wrap;
    }
    &__title {
      margin: 0;
      font-weight: 500;
    }
    &__subtitle {
      margin: 0 0 $base-space * 3 0;
      font-weight: 300;
    }
    &__cards {
      display: flex;
      flex-direction: column;
      gap: $base-space * 2;
    }
  }
}
</style>
