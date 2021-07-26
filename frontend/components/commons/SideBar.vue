<template>
  <aside :class="['sidebar', annotationEnabled ? 'annotation' : 'explore']">
    <p
      v-if="!visible"
      class="sidebar__show-button"
      @click="toggleVisibleMetrics"
    >
      <svgicon name="metrics" width="30" height="30" color="#4C4EA3" />
    </p>
    <div v-show="visible" class="sidebar__wrapper">
      <div class="sidebar__content">
        <svgicon
          class="sidebar__close-button"
          name="cross"
          width="16"
          height="16"
          color="#4C4EA3"
          @click="toggleVisibleMetrics"
        />
        <slot></slot>
      </div>
      <div v-if="annotationEnabled">
        <ReButton
          class="button-clear button-action global-actions__export"
          @click="onOpenExportModal()"
        >
          <svgicon name="export" width="14" height="14" color="#0508D9" />Create
          snapshot
        </ReButton>
        <ReModal
          :modal-custom="true"
          :prevent-body-scroll="true"
          modal-class="modal-primary"
          :modal-visible="openExportModal"
          modal-position="modal-center"
          @close-modal="closeModal()"
        >
          <p class="modal__title">Confirm snapshot creation</p>
          <p class="modal__text">
            You are about to export {{ annotationsSum }} annotations. You will
            find the file on the server once the action is completed.
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
    </div>
  </aside>
</template>
<script>
import { mapActions } from "vuex";
import "assets/icons/metrics";
import "assets/icons/cross";
export default {
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
  computed: {
    annotationsSum() {
      return this.dataset.results.aggregations.status ? this.dataset.results.aggregations.status.Validated : 0;
    },
    annotationEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
    },
  },
  watch: {
    async datasetName() {
      this.$fetch();
    },
  },
  methods: {
    ...mapActions({
      exportAnnotations: "entities/datasets/exportAnnotations",
    }),
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
    toggleVisibleMetrics() {
      this.visible = !this.visible;
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
    box-shadow: 0 5px 11px 0 rgba(0, 0, 0, 0.5);
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
    @include media(">desktopLarge") {
      display: none;
    }
  }
  &__close-button {
    position: absolute;
    top: 1.5em;
    right: 2em;
    cursor: pointer;
    @include media(">desktopLarge") {
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
    box-shadow: 0 5px 11px 0 rgba(0, 0, 0, 0.5);
    max-height: calc(100% - 160px);
    overflow: auto;
    transition: top 0.2s ease-in-out;
    .annotation & {
      margin-top: -4.5em;
    }
    .explore & {
      margin-top: 1em;
    }
    @include media(">desktopLarge") {
      margin-left: 1em;
      margin-top: 1em;
      display: block !important;
      position: relative;
      right: 0;
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
}
</style>
