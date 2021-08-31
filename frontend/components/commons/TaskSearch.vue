<template>
  <div class="app">
    <div class="app__content">
      <section ref="header" class="header">
        <ReTopbarBrand v-if="currentTask">
          <ReBreadcrumbs :breadcrumbs="breadcrumbs" />
        </ReTopbarBrand>
        <component :is="currentTaskHeader" :dataset="dataset" />
      </section>
      <div class="container">
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
  },
  updated() {
    window.onresize = () => {
      this.width = window.innerWidth;
    };
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
    onRefresh() {
      this.search({
        dataset: this.dataset,
        query: this.dataset.query,
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
  @include grid($flex-wrap: nowrap, $gutter: 2em);
  margin: 0;
  .fixed-header & {
    ::v-deep .virtual-scroll {
      padding-top: 3em;
    }
    .sidebar {
      padding-top: 3em;
      &.TokenClassification {
        padding-top: 7.5em;
      }
    }
  }
  &--editable {
    .fixed-header & {
      ::v-deep .virtual-scroll,
      .sidebar {
        padding-top: 8.4em;
      }
      .sidebar {
        padding-top: 8.4em;
        &.TokenClassification {
          padding-top: 12.4em;
        }
      }
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
  .fixed-header & {
    // top: -265px;
    // transition: transform 0.2s ease-in-out;
    // transform: translateY(10px);
    position: fixed;
    background: $bg;
    z-index: 2;
    box-shadow: 1px 1px 6px $font-medium-color;
    ::v-deep .filters,
    ::v-deep .filters__switch,
    ::v-deep .filter--sort,
    ::v-deep .filters__title,
    ::v-deep .topbar {
      display: none;
    }
    ::v-deep .filters__content {
      padding: 0;
    }
    ::v-deep .global-actions {
      margin-top: 0;
      padding-top: 0;
      background: $bg;
      border: none;
      min-height: 70px;
    }
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
