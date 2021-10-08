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
  <div v-if="annotationsProgress">
    <p class="sidebar__title">Annotation progress</p>
    <div class="progress__info">
      <p class="progress__info__text">Total annotations</p>
      <span class="progress__info__percent">{{ progress | percent }}</span>
    </div>
    <div class="progress__numbers">
      <span>{{ totalAnnotated | formatNumber }}</span
      >/{{ total | formatNumber }}
    </div>
    <ReProgress
      re-mode="determinate"
      :multiple="true"
      :progress="(totalValidated * 100) / total"
      :progress-secondary="(totalDiscarded * 100) / total"
    ></ReProgress>
    <div class="scroll">
      <div>
        <div class="info">
          <span class="color-bullet validated"></span>
          <label>Validated</label>
          <span class="records-number">
            {{ totalValidated | formatNumber }}
          </span>
        </div>
        <div class="info">
          <span class="color-bullet discarded"></span>
          <label>Discarded</label>
          <span class="records-number">
            {{ totalDiscarded | formatNumber }}
          </span>
        </div>
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script>
import { AnnotationProgress } from "@/models/AnnotationProgress";
export default {
  // TODO clean and typify
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  computed: {
    annotationsSum() {
      return this.dataset.results.aggregations.status.Validated;
    },
    annotationsProgress() {
      return AnnotationProgress.find(this.dataset.name);
    },
    totalValidated() {
      return this.annotationsProgress.validated;
    },
    totalDiscarded() {
      return this.annotationsProgress.discarded;
    },
    totalAnnotated() {
      return this.totalValidated + this.totalDiscarded;
    },
    total() {
      return this.annotationsProgress.total;
    },
    datasetName() {
      return this.dataset.name;
    },
    progress() {
      return (
        ((this.totalValidated || 0) + (this.totalDiscarded || 0)) / this.total
      );
    },
    annotationIsEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
    },
  },
};
</script>
<style lang="scss" scoped>
.sidebar {
  &__title {
    color: $font-secondary-dark;
    margin-top: 0.5em;
    @include font-size(20px);
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
.subtitle {
  display: inline-block;
  margin-top: 3em;
  margin-bottom: 0.5em;
}
.info {
  position: relative;
  display: flex;
  margin-bottom: 0.7em;
  color: $font-secondary-dark;
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
  &__info {
    display: flex;
    @include font-size(15px);
    align-items: center;
    color: $font-secondary-dark;
    &__percent {
      margin-right: 0;
      margin-left: auto;
    }
  }
  &__numbers {
    color: $font-secondary-dark;
    margin-bottom: 1.5em;
    @include font-size(18px);
    span {
      @include font-size(40px);
    }
  }
}
.color-bullet {
  height: 10px;
  width: 10px;
  border-radius: 50%;
  display: inline-block;
  margin: 0.3em 0.3em 0.3em 0;
  &.validated {
    background: #4c4ea3;
  }
  &.discarded {
    background: #a1a2cc;
  }
}
</style>
