<template>
  <div>
    <div
      :class="annotationEnabled ? 'list__item--annotation-mode' : 'list__item'"
    >
      <div
        v-if="annotationEnabled && item.status !== 'Default'"
        class="list__li__status"
      >
        {{ item.status }}
      </div>
      <ReCheckbox
        v-if="annotationEnabled"
        class="list__checkbox"
        :value="item.selected"
        @change="onCheckboxChanged($event, item.id)"
      ></ReCheckbox>
      <slot :record="item" />
      <RecordExtraActions
        :allow-change-status="annotationEnabled"
        :record="item"
        @onChangeRecordStatus="onChangeRecordStatus"
        @onShowMetadata="onShowMetadata"
      />
    </div>
    <LazyReModal
      modal-class="modal-secondary"
      modal-position="modal-center"
      :modal-custom="true"
      :prevent-body-scroll="true"
      :modal-visible="showMetadata"
      @close-modal="closeMetadata"
    >
      <Metadata
        :applied-filters="dataset.query.metadata"
        :metadata-items="item.metadata"
        :inputs="item.inputs"
        @metafilterApply="onApplyMetadataFilter"
        @cancel="closeMetadata"
      />
    </LazyReModal>
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
    item: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      selectedMetadataItem: this.metadataId,
      showMetadata: false,
    };
  },
  computed: {
    annotationEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
    },
    visibleRecords() {
      return this.dataset.visibleRecords;
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateRecords",
      search: "entities/datasets/search",
      editAnnotations: "entities/datasets/editAnnotations",
      discard: "entities/datasets/discardAnnotations",
      validate: "entities/datasets/validateAnnotations",
    }),

    async onApplyMetadataFilter(metadata) {
      this.closeMetadata();
      this.search({
        dataset: this.dataset,
        query: { metadata: metadata },
      });
    },
    async onCheckboxChanged(checkboxStatus, id) {
      const record = this.visibleRecords.find((r) => r.id === id);
      await this.updateRecords({
        dataset: this.dataset,
        records: [{ ...record, selected: checkboxStatus }],
        // TODO: update annotation status if proceed
      });
    },

    async onChangeRecordStatus(status) {
      switch (status) {
        case "Validated":
          await this.validate({
            dataset: this.dataset,
            records: [this.record],
          });
          break;
        case "Discarded":
          await this.discard({
            dataset: this.dataset,
            records: [this.record],
          });
          break;
        case "Edited":
          await this.editAnnotations({
            dataset: this.dataset,
            records: [
              {
                ...this.record,
                status: "Edited",
                annotation: {
                  agent: this.$auth.user,
                  labels: [],
                },
              },
            ],
          });
          break;
        default:
          console.warn("waT?", status);
      }
    },

    onShowMetadata() {
      this.showMetadata = true;
    },
    closeMetadata() {
      this.showMetadata = false;
    },
  },
};
</script>
<style lang="scss" scoped>
.list {
  &__checkbox.re-checkbox {
    position: absolute;
    left: 1.2em;
    top: 1.2em;
    width: auto;
  }
  &__li {
    &__status {
      position: absolute;
      top: 1em;
      right: 1em;
      font-style: italic;
    }
    &.--discarded {
      ::v-deep .record,
      ::v-deep .feedback-interactions {
        opacity: 0.3;
        pointer-events: none;
      }
    }
  }
  &__item {
    position: relative;
    background: $lighter-color;
    border-radius: 3px;
    display: inline-block;
    width: 100%;
    &__asterisk {
      @include font-size(24px);
      color: $secondary-color;
    }
    &--annotation-mode {
      // padding-left: 4em;
      @extend .list__item !optional;
    }
    &__checkbox.re-checkbox {
      position: absolute;
      left: 1.2em;
      top: 1.2em;
      width: auto;
    }
  }
}
.show-record-number {
  position: fixed;
  overflow: scroll;
  top: 7em;
  right: 1em;
  background: $lighter-color;
  border-radius: 10px;
  min-height: 30px;
  line-height: 30px;
  padding: 0 0.5em;
  display: none;
  span {
    @include font-size(20px);
    margin-right: 10px;
    color: $line-smooth-color;
  }
  .fixed-header & {
    display: block;
  }
}

.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}
</style>
