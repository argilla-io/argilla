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
          class="home__header"
          :breadcrumbs="[
            { action: 'clearFilters', name: $t('breadcrumbs.home') },
          ]"
          @breadcrumb-action="onBreadcrumbAction"
        />
        <PersistentStorageBanner class="home__banner" />
        <datasets-table
          class="home__table"
          ref="table"
          :datasets="datasets.datasets"
        />
      </div>
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
    padding: 0 $base-space * 4;
    min-height: 0;
    overflow: auto;
  }
}
</style>
