<template>
  <aside v-click-outside="closeMetrics" class="sidebar">
    <p class="sidebar__show-button" @click="toggleVisibleMetrics">
      <svgicon name="metrics" width="30" height="30" color="#F48E5F" />
    </p>
    <div v-if="visible && annotationsProgress" class="sidebar__wrapper">
      <div class="sidebar__content">
        <p>Annotations</p>
        <span class="progress progress--percent">{{ progress }}%</span>
        <ReProgress
          re-mode="determinate"
          :multiple="true"
          :progress="(totalValidated * 100) / total"
          :progress-secondary="(totalDiscarded * 100) / total"
        ></ReProgress>
        <div class="scroll">
          <div class="info">
            <label>All</label>
            <span class="records-number">
              <strong>{{ total }}</strong>
            </span>
          </div>
          <div class="info">
            <label>Validated</label>
            <span class="records-number">
              <strong>{{ totalValidated }}</strong>
            </span>
          </div>
          <div class="info">
            <label>Discarded</label>
            <span class="records-number">
              <strong>{{ totalDiscarded }}</strong>
            </span>
          </div>
          <div
            v-for="(counter, label) in annotationsProgress.annotatedAs"
            :key="label"
          >
            <div v-if="counter > 0" class="info">
              <label>{{ label }}</label>
              <span class="records-number">{{ counter }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>
<script>
import "assets/icons/export";
import "assets/icons/metrics";

import { AnnotationProgress } from "@/models/AnnotationProgress";
import { ObservationDataset } from "@/models/Dataset";
export default {
  // TODO clean and typify
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },

  data: () => ({
    visible: false,
    preventCloseOnClickOutside: true,
  }),
  async fetch() {
    await ObservationDataset.dispatch("refreshAnnotationProgress", {
      dataset: this.dataset,
    });
  },
  computed: {
    annotationsProgress() {
      return AnnotationProgress.find(this.dataset.name + this.dataset.task);
    },
    totalValidated() {
      return this.annotationsProgress.validated;
    },
    totalDiscarded() {
      return this.annotationsProgress.discarded;
    },
    total() {
      return this.annotationsProgress.total;
    },
    datasetName() {
      return this.dataset.name;
    },
    datasetTask() {
      return this.dataset.task;
    },
    progress() {
      return (
        ((this.totalValidated || 0) +
        (this.totalDiscarded || 0)) * 100 / this.total
      ).toFixed(2);
    },
  },

  watch: {
    async datasetName() {
      this.$fetch();
    },
    async datasetTask() {
      this.$fetch();
    },
  },

  methods: {
    closeMetrics() {
      this.visible = this.preventCloseOnClickOutside;
    },
    toggleVisibleMetrics() {
      !this.visible ? (this.visible = true) : (this.visible = false);
    },
  },
};
</script>
<style lang="scss" scoped>
.sidebar {
  margin-top: 2em;
  z-index: 0;
  &__show-button {
    position: absolute;
    right: 3em;
    cursor: pointer;
    text-align: right;
  }
  &__wrapper {
    min-width: 200px;
    max-width: 200px;
    position: absolute;
    right: 1em;
    margin-top: 4em;
    // display: none;
    background: white;
    padding: 1em;
    box-shadow: $shadow;
    .fixed-header & {
      // position: fixed;
      width: 100%;
      max-width: 200px;
      max-height: calc(100% - 180px);
      overflow: auto;
      transition: top 0.2s ease-in-out;
      padding-right: 1em;
    }
  }
  &__content {
    border-bottom: 1px solid $line-smooth-color;
    padding: 1em 0 2em 0;
    margin-bottom: 1.8em;
    border-radius: 2px;
    &:first-child {
      padding-top: 0;
    }
    p {
      @include font-size(18px);
      margin-top: 0;
      font-weight: 600;
    }
  }
  .re-progress {
    width: calc(100% - 90px);
    &--multiple {
      width: calc(100% - 90px);
    }
  }
  label {
    margin-top: 1.2em;
    margin-bottom: 0.5em;
    display: block;
    width: calc(100% - 40px);
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .total {
    font-weight: 600;
    max-width: 100%;
    width: 100%;
    margin-bottom: 1em;
  }
  .info {
    @include font-size(13px);
    position: relative;
    display: flex;
    margin-bottom: 0.7em;
    max-height: 50vh;
    overflow: scroll;
    label {
      margin: 0; // for tagger
      &[class^="color_"] {
        padding: 0.3em;
      }
    }
  }
  .scroll {
    max-height: calc(100vh - 340px);
    padding-right: 1em;
    margin-right: -1em;
    overflow: auto;
  }
  .records-number {
    margin-right: 0;
    margin-left: auto;
    font-weight: bold;
  }
  .progress__block {
    margin-bottom: 2.5em;
    position: relative;
    &:last-of-type {
      margin-bottom: 0;
    }
    &.loading-skeleton {
      opacity: 0;
    }
    .re-progress {
      margin-bottom: 0.5em;
    }
    p {
      @include font-size(18px);
      margin-top: 0;
      font-weight: 600;
      &:not(.button) {
        pointer-events: none;
      }
    }
    .button-icon {
      color: $primary-color;
      padding: 0;
      display: flex;
      margin-left: auto;
      margin-right: 0;
      margin-top: 2em;
      .svg-icon {
        fill: $primary-color;
        margin-left: 1em;
      }
    }
  }
  .progress {
    float: right;
    line-height: 0.8em;
    @include font-size(13px);
    font-weight: bold;
  }
}
</style>
