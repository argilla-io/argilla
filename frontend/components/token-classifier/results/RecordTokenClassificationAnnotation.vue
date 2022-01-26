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
    <text-spans
      :dataset="dataset"
      :record="record"
      :entities="annotationEntities"
      @updateRecordEntities="updateRecordEntities"
    />
    <div class="content__actions-buttons">
      <re-button
        v-if="record.status !== 'Validated'"
        class="button-primary"
        @click="onValidate(record)"
        >{{ record.status === "Edited" ? "Save" : "Validate" }}</re-button
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
  computed: {
    annotationEntities() {
      let entities = [];
      if (this.record.annotation) {
        entities = this.record.annotation.entities.map((obj) => ({
          ...obj,
          origin: "annotation",
        }));
      } else if (this.record.prediction) {
        entities = this.record.prediction.entities.map((obj) => ({
          ...obj,
          origin: "prediction",
        }));
      }
      return entities;
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
      validate: "entities/datasets/validateAnnotations",
    }),
    updateRecordEntities(entities) {
      this.updateRecords({
        dataset: this.dataset,
        records: [
          {
            ...this.record,
            selected: true,
            status: "Edited",
            annotation: {
              entities,
              agent: this.$auth.user.username,
            },
          },
        ],
      });
      // this.onReset();
    },
    async onValidate(record) {
      const emptyEntities = {
        entities: [],
      };
      await this.validate({
        dataset: this.dataset,
        agent: this.$auth.user.username,
        records: [
          {
            ...record,
            annotation: {
              ...(record.annotation || record.prediction || emptyEntities),
            },
          },
        ],
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.content {
  position: relative;
  white-space: pre-wrap;
  & > div:nth-child(2) {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    ::v-deep {
      .span__text {
        opacity: 0;
      }
    }
  }
  &__input {
    padding-right: 200px;
  }
  &__actions-buttons {
    margin-right: 0;
    margin-left: auto;
    display: flex;
    min-width: 20%;
    .re-button {
      min-height: 32px;
      line-height: 32px;
      display: block;
      margin: 1.5em auto 0 0;
      & + .re-button {
        margin-left: 1em;
      }
    }
  }
}
</style>
