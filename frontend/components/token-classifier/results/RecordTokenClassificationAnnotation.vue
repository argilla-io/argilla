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
    <div class="origins">
      <text-spans-static
        v-if="record.prediction"
        v-once
        key="prediction"
        :dataset="dataset"
        origin="prediction"
        :record="record"
        class="prediction"
        :entities="getEntitiesByOrigin('prediction')"
      />
      <text-spans
        key="annotation"
        :dataset="dataset"
        origin="annotation"
        :record="record"
        class="annotation"
        :entities="getEntitiesByOrigin('annotation')"
      />
    </div>
    <div class="content__actions-buttons" v-if="record.status !== 'Validated'">
      <re-button class="button-primary" @click="onValidate(record)">{{
        record.status === "Edited" ? "Save" : "Validate"
      }}</re-button>
      <re-button
        :disabled="!record.annotatedEntities.length"
        class="button-primary--outline"
        @click="onClearAnnotations()"
        >Clear annotations</re-button
      >
    </div>
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
    record: {
      type: Object,
      required: true,
    },
  },
  methods: {
    ...mapActions({
      validate: "entities/datasets/validateAnnotations",
      updateRecords: "entities/datasets/updateDatasetRecords",
    }),
    getEntitiesByOrigin(origin) {
      return origin === "annotation"
        ? this.record.annotatedEntities
        : (this.record.prediction && this.record.prediction.entities) || [];
    },
    async onValidate(record) {
      await this.validate({
        // TODO: Move this as part of token classification dataset logic
        dataset: this.dataset,
        agent: this.$auth.user.username,
        records: [
          {
            ...record,
            annotatedEntities: undefined,
            annotation: {
              entities: record.annotatedEntities,
              origin: "annotation",
            },
          },
        ],
      });
    },
    onClearAnnotations() {
      this.updateRecords({
        dataset: this.dataset,
        records: [
          {
            ...this.record,
            selected: true,
            status: "Edited",
            annotatedEntities: [],
          },
        ],
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.content {
  &__input {
    padding-right: 200px;
    // display: flex;
    // flex-wrap: wrap;
  }
  &__actions-buttons {
    margin-right: 0;
    margin-left: auto;
    display: flex;
    min-width: 20%;
    .re-button {
      min-width: 137px;
      min-height: 34px;
      line-height: 34px;
      display: inline-block;
      margin: 1.5em 0 0 0;
      & + .re-button {
        margin-left: 1em;
      }
    }
  }
}
.origins > .prediction {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  ::v-deep {
    .span__text {
      color: transparent;
      & > * {
        color: palette(grey, dark);
      }
    }
    .highlight__content {
      color: transparent;
    }
  }
  ::v-deep .highlight-text {
    opacity: 1;
  }
}
</style>
