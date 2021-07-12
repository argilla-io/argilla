<template>
  <div v-if="!$fetchState.pending">
    <p>
      <svgicon name="metrics" width="24" height="24" color="#4C4EA3" />{{
        getTitle
      }}
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
    <div v-else>
      <div class="sidebar__tabs">
        <a
          href="#"
          :class="activeTab === 'predicted_mentions' ? 'active' : ''"
          @click.prevent="filteredMentionsBy('predicted_mentions')"
          >Predicted as</a
        >
        <a
          href="#"
          :class="activeTab === 'mentions' ? 'active' : ''"
          @click.prevent="filteredMentionsBy('mentions')"
          >Annotated as</a
        >
      </div>
      <div class="scroll">
        <div v-if="!existMentions">
          <span class="sidebar__tabs__empty"
            >There are no
            {{ activeTab === "mentions" ? "annotations" : "predictions" }}</span
          >
        </div>
        <div
          v-for="(prop, key) in filteredMentions"
          v-else
          :key="key"
          :class="expandedMentionsGroup === key ? 'expanded' : ''"
        >
          <span
            :class="[
              `color_${entities.filter((e) => e.text === key)[0].colorId}`,
              'entity',
            ]"
            >{{ key }}</span
          >
          <SidebarCollapsableMentions
            :limit="
              expandedMentionsGroup && expandedMentionsGroup !== key
                ? 0
                : currentMentionsLength
            "
            :entities="entities"
            :k="key"
            :object="filteredMentions"
            @limit="onShowMore(key)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { AnnotationProgress } from "@/models/AnnotationProgress";
import { ObservationDataset } from "@/models/Dataset";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    limit: 3,
    currentMentionsLength: 3,
    visible: false,
    activeTab: "mentions",
    filteredMentions: [],
    expandedMentionsGroup: undefined,
  }),
  async fetch() {
    await ObservationDataset.dispatch("refreshAnnotationProgress", {
      dataset: this.dataset,
    });
  },
  computed: {
    existMentions() {
      return Object.keys(this.filteredMentions).length;
    },
    datasetName() {
      return this.dataset.name;
    },
    entities() {
      return this.dataset.entities;
    },
    getTitle() {
      return this.annotationIsEnabled ? "Annotations" : "Mentions";
    },
    annotationsSum() {
      return this.dataset.results.aggregations.status.Validated;
    },
    annotationsProgress() {
      return AnnotationProgress.find(this.dataset.name + this.dataset.task);
    },
    annotationIsEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
    },
    getInfo() {
      return this.annotationIsEnabled
        ? this.annotationsProgress.annotatedAs
        : this.dataset.results.aggregations.words;
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
    progress() {
      return (
        (((this.totalValidated || 0) + (this.totalDiscarded || 0)) * 100) /
        this.total
      ).toFixed(2);
    },
  },

  watch: {
    async datasetName() {
      this.$fetch();
    },
  },
  mounted() {
    this.filteredMentions = this.dataset.results.aggregations[this.activeTab];
  },

  methods: {
    filteredMentionsBy(type) {
      this.activeTab = type;
      this.filteredMentions = this.dataset.results.aggregations[type];
      this.expandedMentionsGroup = undefined;
      this.currentMentionsLength = this.limit;
    },
    onShowMore(k) {
      const itemsLenght = Object.keys(this.filteredMentions[k]).length;
      this.currentMentionsLength === this.limit
        ? (this.currentMentionsLength = itemsLenght)
        : (this.currentMentionsLength = this.limit);
      this.currentMentionsLength === itemsLenght
        ? (this.expandedMentionsGroup = k)
        : (this.expandedMentionsGroup = undefined);
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
.sidebar {
  &__tabs {
    display: flex;
    padding-bottom: 1em;
    &__empty {
      margin-top: 2em;
      display: inline-block;
    }
    a {
      width: 100%;
      border: 1px solid palette(grey, smooth);
      border-radius: 2px;
      text-align: center;
      color: $font-secondary;
      text-decoration: none;
      margin: 0 5px;
      outline: none;
      @include font-size(13px);
      padding: 0.3em;
      &.active {
        background: palette(grey, light);
      }
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
  .entity {
    margin-top: 1em;
    margin-bottom: 0.5em;
    padding: 0.5em;
    display: inline-flex;
  }
  .scroll {
    max-height: calc(100vh - 400px);
    padding-right: 1em;
    margin-right: -1em;
    overflow: auto;
  }
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
$colors: 40;
$hue: 360;
@for $i from 1 through $colors {
  $rcolor: hsla(($colors * $i) + ($hue * $i / $colors), 100%, 82%, 1);
  .color_#{$i - 1} {
    background: $rcolor;
  }
}
</style>
