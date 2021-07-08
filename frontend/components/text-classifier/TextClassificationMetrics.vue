<template>
  <div v-if="!$fetchState.pending">
    <p>
      <svgicon name="metrics" width="24" height="24" color="#4C4EA3" />
      {{ getTitle }}
    </p>
    <div v-if="annotationIsEnabled">
      <span class="progress progress--percent">{{ progress }}%</span>
      <ReProgress
        re-mode="determinate"
        :multiple="true"
        :progress="(totalValidated * 100) / total"
        :progress-secondary="(totalDiscarded * 100) / total"
      ></ReProgress>
      <div class="scroll">
        <div>
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
          <div class="labels">
            <div v-for="(counter, label) in getInfo" :key="label">
              <div v-if="counter > 0" class="info">
                <label>{{ label }}</label>
                <span class="records-number">{{ counter }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="scroll">
      <div v-for="(counter, keyword) in getKeywords" :key="keyword">
        <div v-if="counter > 0" class="info">
          <label>{{ keyword }}</label>
          <span class="records-number">{{ counter }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import "assets/icons/export";
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
  async fetch() {
    await ObservationDataset.dispatch("refreshAnnotationProgress", {
      dataset: this.dataset,
    });
  },
  computed: {
    annotationsSum() {
      return this.dataset.results.aggregations.status.Validated;
    },
    annotationsProgress() {
      return AnnotationProgress.find(this.dataset.name + this.dataset.task);
    },
    getInfo() {
      return this.annotationIsEnabled
        ? this.annotationsProgress.annotatedAs
        : this.dataset.results.aggregations.words;
    },
    getTitle() {
      return this.annotationIsEnabled ? "Annotations" : "Keywords";
    },
    getKeywords() {
      return this.dataset.results.aggregations.words;
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
    progress() {
      return (
        (((this.totalValidated || 0) + (this.totalDiscarded || 0)) * 100) /
        this.total
      ).toFixed(2);
    },
    annotationIsEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
    },
  },

  watch: {
    async datasetName() {
      this.$fetch();
    },
  },
};
</script>
<style lang="scss" scoped>
.re-progress {
  width: calc(100% - 90px);
  &--multiple {
    width: calc(100% - 90px);
  }
}
p {
  display: flex;
  align-items: flex-end;
  font-size: 18px;
  font-size: 1.125rem;
  margin-top: 0;
  margin-bottom: 2em;
  font-weight: 600;
  svg {
    margin-right: 0.5em;
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
.labels {
  margin-top: 3em;
  strong {
    margin-bottom: 1em;
    display: block;
  }
}
.total {
  font-weight: 600;
  max-width: 100%;
  width: 100%;
  margin-bottom: 1em;
}
.subtitle {
  display: inline-block;
  margin-top: 3em;
  margin-bottom: 0.5em;
}
.info {
  position: relative;
  display: flex;
  margin-bottom: 0.7em;
  label {
    margin: 0; // for tagger
    &[class^="color_"] {
      padding: 0.3em;
    }
  }
}
.scroll {
  max-height: calc(100vh - 400px);
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
  font-weight: bold;
}
</style>
