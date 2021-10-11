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
    ]"
  >
    <div class="app__content">
      <section id="header" ref="header" class="header">
        <ReTopbarBrand v-if="currentTask">
          <ReBreadcrumbs :breadcrumbs="breadcrumbs" />
        </ReTopbarBrand>
        <component :is="currentTaskHeader" :dataset="dataset" />
      </section>
      <div :class="['grid', annotationEnabled ? 'grid--editable' : '']">
        <Results :dataset="dataset" />
        <SideBarPanel
          v-if="sidebarVisible || width > 1500"
          :dataset="dataset"
          :class="dataset.task"
        >
          <div v-show="sidebarInfoType === 'progress'">
            <component :is="currentTaskProgress" :dataset="dataset" />
          </div>
          <div v-show="sidebarInfoType === 'stats'">
            <component :is="currentTaskStats" :dataset="dataset" />
          </div>
        </SideBarPanel>
      </div>
    </div>
    <sidebar
      :dataset="dataset"
      @refresh="onRefresh"
      @showSidebarInfo="onShowSidebarInfo"
      @onChangeMode="onChangeMode"
    />
  </div>
</template>
<script>
import { mapActions } from "vuex";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    sidebarInfoType: "progress",
    sidebarVisible: false,
    width: window.innerWidth,
    headerHeight: undefined,
  }),
  computed: {
    currentTask() {
      return this.dataset.task;
    },
    breadcrumbs() {
      return [
        { link: { path: "/" }, name: "Datasets" },
        { link: this.$route.fullPath, name: this.dataset.name },
      ];
    },
    currentTaskHeader() {
      return this.currentTask + "Header";
    },
    currentTaskProgress() {
      return this.currentTask + "Progress";
    },
    currentTaskStats() {
      return this.currentTask + "Stats";
    },
    annotationEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
    },
    globalHeaderHeight() {
      return this.dataset.viewSettings.headerHeight
    }
  },
  updated() {
    window.onresize = () => {
      this.width = window.innerWidth;
    };
  },
  mounted() {
    this.setHeaderHeight();
  },
  watch: {
    globalHeaderHeight() {
      if (this.globalHeaderHeight !== this.headerHeight) {
        this.headerHeightUpdate();
      }
    }
  },
  methods: {
    ...mapActions({
      fetchDataset: "entities/datasets/fetchByName",
      enableAnnotation: "entities/datasets/enableAnnotation",
      search: "entities/datasets/search",
    }),
    async onChangeMode() {
      await this.enableAnnotation({
        dataset: this.dataset,
        value: this.annotationEnabled ? false : true,
      });
    },
    async setHeaderHeight() {
      const header = this.$refs.header;
      const resize_ob = new ResizeObserver(() => {
        this.headerHeight = header.offsetHeight;
        this.headerHeightUpdate();
      });
      resize_ob.observe(header);
    },
    onRefresh() {
      this.search({
        dataset: this.dataset,
        query: this.dataset.query,
      });
    },
    headerHeightUpdate() {
      DatasetViewSettings.update({
        where: this.dataset.name,
        data: {
          headerHeight: this.headerHeight,
        },
      });
    },
    onShowSidebarInfo(info) {
      if (this.sidebarInfoType !== info) {
        this.sidebarVisible = true;
      } else {
        this.sidebarVisible = !this.sidebarVisible;
      }
      this.sidebarInfoType = info;
    },
  },
};
</script>
<style lang="scss" scoped>
.app {
  display: flex;
  &__content {
    width: 100%;
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
  .fixed-header & {
    ::v-deep .virtual-scroll {
      padding-top: 3em;
    }
  }
}

.header {
  opacity: 1;
  z-index: 1;
  position: relative;
  transition: none;
  top: 0;
  right: 0;
  left: 0;
  transform: translateY(0);
  position: fixed;
  background: $bg;
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
