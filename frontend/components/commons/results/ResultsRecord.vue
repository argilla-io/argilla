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
  <div>
    <div
      :class="[
        annotationEnabled ? 'list__item--annotation-mode' : 'list__item',
        item.status === 'Discarded' ? 'discarded' : null,
      ]"
    >
      <!-- TODO: make global, remove task reference -->
      <div
        v-if="
          annotationEnabled &&
          item.status !== 'Default' &&
          dataset.task !== 'Text2Text'
        "
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
        :task="dataset.task"
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
        :title="item.recordTitle()"
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
      updateRecords: "entities/datasets/updateDatasetRecords",
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

    async onChangeRecordStatus(status, record) {
      switch (status) {
        case "Validated":
          await this.validate({
            dataset: this.dataset,
            records: [record],
          });
          break;
        case "Discarded":
          await this.discard({
            dataset: this.dataset,
            records: [record],
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
  }
  &__item {
    position: relative;
    background: $lighter-color;
    border-radius: 3px;
    display: inline-block;
    width: 100%;
    transition: 0.3s ease-in-out;
    border: 1px solid white;
    &:hover {
      border: 1px solid palette(grey, smooth);
      .record__extra-actions--text2text {
        opacity: 1;
        pointer-events: all;
      }
    }
    &__asterisk {
      @include font-size(24px);
      color: $secondary-color;
    }
    &--annotation-mode {
      // padding-left: 4em;
      @extend .list__item !optional;
      &.discarded {
        opacity: 0.5;
        transition: 0.3s ease-in-out;
        &:hover {
          opacity: 1;
          transition: 0.3s ease-in-out;
        }
      }
    }
    &__checkbox.re-checkbox {
      position: absolute;
      left: 1.2em;
      top: 1.2em;
      width: auto;
    }
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
