<template>
  <div>
    <aside class="sidebar">
        <div class="sidebar__wrapper">
          <!-- <div class="sidebar__content" v-if="metrics.annotated">
            <div
              :class="['progress__block', loadingQ ? 'loading-skeleton' : '']"
            >
              <p>Annotation</p>
              <div class="total">
                <span class="progress">{{ feedbackProgress }}%</span>
                <ReProgress
                  re-mode="determinate"
                  :progress="parseFloat(feedbackProgress)"
                />
              </div>

              <span
                v-for="(metric, key) in metricsOverall"
                :key="key"
                class="info"
              >
                <label>{{ metric.key }}</label>
                <span class="records-number">{{ metric.value }}</span>
              </span>
            </div>
            <ReButton
              v-if="metrics.annotated"
              class="button-clear button-action"
              @click="onOpenExportModal()"
            >
              <svgicon
                name="export"
                width="14"
                height="14"
                color="#F48E5F"
              />Export annotations
            </ReButton>
          </div> -->
        </div>
    </aside>
    <!-- <ReModal
      v-if="metrics.annotated"
      :modal-custom="true"
      :prevent-body-scroll="true"
      modal-class="modal-primary"
      :modal-visible="openExportModal"
      modal-position="modal-center"
      @close-modal="closeModal()"
    >
      <p class="modal__title">Confirm export of annotations</p>
      <p class="modal__text">
        You are about to export {{ metrics.annotated }} annotations. You will
        find the file on the server once the action is completed.
      </p>
      <div class="modal-buttons">
        <ReButton
          class="button-tertiary--small button-tertiary--outline"
          @click="closeModal()"
        >
          Cancel
        </ReButton>
        <ReButton class="button-secondary--small" @click="onExportAnnotations()">
          Confirm export
        </ReButton>
      </div>
    </ReModal> -->
  </div>
</template>
<script>
import "assets/icons/export";

export default {
  // TODO clean and typify
  props: {
    metrics: {
      type: Object,
    },
    loadingQ: {
      type: Boolean,
      default: false,
    },
  },
  data: () => ({
    openExportModal: false,
  }),
  computed: {
    metricsOverall() {
      return Object.entries(this.metrics).map(([key, value]) => ({
        key,
        value,
      }));
    },
    feedbackProgress() {
      if (this.metrics.annotated) {
        return ((this.metrics.annotated * 100) / this.metrics.total).toFixed(2);
      }
    },
  },
  methods: {
    onOpenExportModal() {
      this.openExportModal = true;
    },
    closeModal() {
      this.openExportModal = false;
    },
    onExportAnnotations() {
      this.openExportModal = false;
      console.log("export");
      // this.apiClient().exportAnnotations(this.project, this.prediction)
      //   .then((path) => {
      //     Vue.$toast.open({
      //       message: `The export is finished, the file is accessible at file://${path}`,
      //       type: 'default',
      //     });
      //   })
      //   .catch((error) => {
      //     Vue.$toast.open({
      //       message: error,
      //       type: 'warning',
      //     });
      //   });
    },
  },
};
</script>
<style lang="scss" scoped>
.sidebar {
  @include grid-col($col: 3, $gutter: 1.6em);
  // margin-top: 2em;
  min-width: 270px;
  max-width: 270px;
  margin-left: 3em;
  z-index: 0;
  &__wrapper {
    .fixed-header & {
      position: fixed;
      width: 100%;
      max-width: 270px;
      max-height: calc(100% - 180px);
      overflow: auto;
      top: 9em;
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
    @include font-size(13px);
    font-weight: bold;
  }
}
</style>
