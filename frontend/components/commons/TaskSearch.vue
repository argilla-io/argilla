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
  <div
    :class="[
      'app',
      currentTask,
      annotationEnabled ? '--annotation' : '--exploration',
      areMetricsVisible ? '--metrics' : null,
    ]"
  >
    <div class="app__content">
      <section id="header" ref="header" class="header">
        <ReTopbarBrand v-if="currentTask">
          <ReBreadcrumbs :breadcrumbs="breadcrumbs" :copy-button="true" />
          <user />
        </ReTopbarBrand>
        <task-sidebar :dataset="dataset" />
        <component :is="currentTaskHeader" :dataset="dataset" />
      </section>
      <div :class="['grid', annotationEnabled ? 'grid--editable' : '']">
        <Results :dataset="dataset" />
      </div>
    </div>
  </div>
</template>
<script>
import "assets/icons/copy";
import { mapActions } from "vuex";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
import { currentWorkspace, workspaceHome } from "@/models/Workspace";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    headerHeight: undefined,
  }),
  computed: {
    currentTask() {
      return this.dataset.task;
    },
    breadcrumbs() {
      return [
        { link: { path: workspaceHome(this.workspace) }, name: this.workspace },
        { link: this.$route.fullPath, name: this.dataset.name },
      ];
    },
    areMetricsVisible() {
      return this.dataset.viewSettings.visibleMetrics;
    },
    currentTaskHeader() {
      return this.currentTask + "Header";
    },
    annotationEnabled() {
      return this.dataset.viewSettings.viewMode === "annotate";
    },
    globalHeaderHeight() {
      return this.dataset.viewSettings.headerHeight;
    },
    currentViewMode() {
      return this.dataset.viewSettings.viewMode;
    },
    workspace() {
      return currentWorkspace(this.$route);
    },
  },
  watch: {
    globalHeaderHeight() {
      if (this.globalHeaderHeight !== this.headerHeight) {
        this.headerHeightUpdate();
      }
    },
    async currentViewMode(n) {
      if (n === "labelling-rules") {
        await this.resetSearch({ dataset: this.dataset });
      }
    },
  },
  mounted() {
    this.setHeaderHeight();
  },
  methods: {
    ...mapActions({
      resetSearch: "entities/datasets/resetSearch",
      fetchDataset: "entities/datasets/fetchByName",
    }),
    async setHeaderHeight() {
      const header = this.$refs.header;
      const resize_ob = new ResizeObserver(() => {
        this.headerHeight = header.offsetHeight;
        this.headerHeightUpdate();
      });
      resize_ob.observe(header);
    },
    headerHeightUpdate() {
      DatasetViewSettings.update({
        where: this.dataset.name,
        data: {
          headerHeight: this.headerHeight,
        },
      });
    },
  },
};
</script>
<style lang="scss" scoped>
.app {
  display: flex;
  &__content {
    width: 100%;
    .fixed-header & {
      z-index: 3;
    }
  }
}
.container {
  @extend %container;
  padding-top: 0;
  padding-bottom: 0;
  margin-left: 0;
  &--intro {
    padding-top: 2em;
    margin-bottom: 1.5em;
    &:after {
      border-bottom: 1px solid $line-light-color;
      content: "";
      margin-bottom: 1.5em;
      position: absolute;
      left: 0;
      right: 0;
    }
  }
}

.grid {
  position: relative;
  margin: 0;
  z-index: 0;
  .--fixed:not(.fixed-header) & {
    z-index: 2;
  }
}

.header {
  opacity: 1;
  position: relative;
  transition: none;
  top: 0;
  right: 0;
  left: 0;
  transform: translateY(0);
  position: fixed;
  background: $bg;
  z-index: 1;
  ::v-deep .header__filters {
    position: relative;
  }
  .fixed-header & {
    animation: header-fixed 0.3s ease-in-out;
    z-index: 2;
    box-shadow: 1px 1px 6px $font-medium-color;
    ::v-deep .filters__title,
    ::v-deep .topbar {
      display: none;
    }
    ::v-deep .global-actions {
      margin-top: 0;
      padding-top: 0;
      background: $bg;
      border: none;
      min-height: 60px;
    }
  }
  .fixed-header .--annotation & {
    ::v-deep .filters__area {
      display: none;
    }
  }
}

@keyframes header-fixed {
  0% {
    transform: translateY(-150px);
  }
  100% {
    transform: translateY(0);
  }
}

.switch-button {
  border: none;
  background: lighten($primary-color, 20%);
  color: $lighter-color;
  outline: none;
  padding: 0.5em 1em;
  cursor: pointer;
  &:last-of-type {
    margin-right: 2em;
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
  }
  &:first-of-type {
    border-top-left-radius: 5px;
    border-bottom-left-radius: 5px;
  }
  &.selected {
    background: $primary-color;
  }
}
</style>
