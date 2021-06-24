<template>
  <aside :class="['sidebar', annotationIsEnabled ? 'annotation' : 'explore']">
    <p v-if="!visible" class="sidebar__show-button" @click="toggleVisibleMetrics">
      <svgicon name="metrics" width="30" height="30" color="#4C4EA3" />
    </p>
    <div v-if="annotationsProgress" v-show="visible" class="sidebar__wrapper">
      <div class="sidebar__content">
        <p><svgicon name="metrics" width="24" height="24" color="#4C4EA3" /> {{ getTitle }}</p>
        <svgicon class="sidebar__close-button" @click="toggleVisibleMetrics" name="cross" width="16" height="16" color="#4C4EA3" />
        <span v-if="annotationIsEnabled" class="progress progress--percent">{{ progress }}%</span>
        <ReProgress
          v-if="annotationIsEnabled"
          re-mode="determinate"
          :multiple="true"
          :progress="(totalValidated * 100) / total"
          :progress-secondary="(totalDiscarded * 100) / total"
        ></ReProgress>
        <div class="scroll">
          <div v-if="annotationIsEnabled" class="info">
            <label>All</label>
            <span class="records-number">
              <strong>{{ total }}</strong>
            </span>
          </div>
          <div v-if="annotationIsEnabled" class="info">
            <label>Validated</label>
            <span class="records-number">
              <strong>{{ totalValidated }}</strong>
            </span>
          </div>
          <div v-if="annotationIsEnabled" class="info">
            <label>Discarded</label>
            <span class="records-number">
              <strong>{{ totalDiscarded }}</strong>
            </span>
          </div>
          <div class="labels">
            <div
              v-for="(counter, label) in getInfo"
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
      <ReButton v-if="annotationIsEnabled"
        class="button-clear button-action global-actions__export"
        @click="onOpenExportModal()"
      >
        <svgicon name="export" width="14" height="14" color="#0508D9" />Create snapshot
      </ReButton>
      <ReModal
        v-if="annotationIsEnabled"
        :modal-custom="true"
        :prevent-body-scroll="true"
        modal-class="modal-primary"
        :modal-visible="openExportModal"
        modal-position="modal-center"
        @close-modal="closeModal()"
      >
        <p class="modal__title">Confirm snapshot creation</p>
        <p class="modal__text">
          You are about to export {{ annotationsSum }} annotations. You will find
          the file on the server once the action is completed.
        </p>
        <div class="modal-buttons">
          <ReButton
            class="button-tertiary--small button-tertiary--outline"
            @click="closeModal()"
          >
            Cancel
          </ReButton>
          <ReButton
            class="button-secondary--small"
            @click="onExportAnnotations()"
          >
            Confirm
          </ReButton>
        </div>
      </ReModal>
    </div>
    <!-- <div v-else-if="dataset.results.aggregations.words" class="sidebar__wrapper">
      <div class="sidebar__content">
        <p><svgicon name="metrics" width="24" height="24" color="#4C4EA3" /> Keywords</p>
        <svgicon class="sidebar__close-button" @click="toggleVisibleMetrics" name="cross" width="16" height="16" color="#4C4EA3" />
        <div class="scroll">
          <div
            v-for="(counter, label) in dataset.results.aggregations.words"
            :key="label"
          >
            <div v-if="counter > 0" class="info">
              <label>{{ label }}</label>
              <span class="records-number">{{ counter }}</span>
            </div>
          </div>
        </div>
      </div>
    </div> -->
  </aside>
</template>
<script>
import "assets/icons/export";
import "assets/icons/metrics";
import "assets/icons/cross";
import { mapActions } from "vuex";
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
    openExportModal: false,
  }),
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
      return this.annotationIsEnabled ? this.annotationsProgress.annotatedAs : this.dataset.results.aggregations.words;
    },
    getTitle() {
      return this.annotationIsEnabled ? 'Annotations' : 'Keywords';
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
    annotationIsEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
    }
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
    ...mapActions({
      exportAnnotations: "entities/datasets/exportAnnotations",
    }),
    toggleVisibleMetrics() {
      !this.visible ? (this.visible = true) : (this.visible = false);
    },
    onOpenExportModal() {
      this.openExportModal = true;
    },
    closeModal() {
      this.openExportModal = false;
    },
    async onExportAnnotations() {
      this.openExportModal = false;
      this.exportAnnotations({ name: this.dataset.name });
    },
  },
};
</script>
<style lang="scss" scoped>
.sidebar {
  z-index: 2;
  &__show-button {
    position: absolute;
    right: 0;
    padding: 1em;
    background: $lighter-color;
    box-shadow: 0 5px 11px 0 rgba(0,0,0,0.50);
    border-top-left-radius: 6px;
    border-bottom-left-radius: 6px;
    cursor: pointer;
    text-align: right;
    .annotation & {
      margin-top: 1em;
    }
    .explore & {
      margin-top: 1em;
    }
    .fixed-header & {
      margin-top: 0;
    }
    @include media('>desktopLarge') {
      display: none;
    }
  }
  &__close-button {
    position: absolute;
    top: 1.5em; 
    right: 2em;
    cursor: pointer;
    @include media('>desktopLarge') {
      display: none;
    }
  }
  &__wrapper {
    border-radius: 5px;
    width: 280px;
    position: absolute;
    right: 1em;
    background: white;
    padding: 1em 2em;
    box-shadow: 0 5px 11px 0 rgba(0,0,0,0.50);
    .annotation & {
      margin-top: -4.5em;
    }
    .explore & {
      margin-top: 1em;
    }
    @include media('>desktopLarge') {
      margin-left: 1em;
      margin-top: 1em;
      display: block !important;
      position: relative;
      right: 0;
    }
    .fixed-header & {
      // position: fixed;
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
      display: flex;
      align-items: flex-end;
      @include font-size(18px);
      margin-top: 0;
      margin-bottom: 2em;
      font-weight: 600;
      svg {
        margin-right: 1em;
      }
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
  .labels {
    margin-top: 3em;
  }
  .total {
    font-weight: 600;
    max-width: 100%;
    width: 100%;
    margin-bottom: 1em;
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
    font-weight: bold;
  }
}
</style>
