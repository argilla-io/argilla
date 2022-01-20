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
  <div class="record">
    <div class="content__toggle" v-if="!annotationEnabled">
      <ReCheckbox
        v-for="option in entitiesOptions"
        :key="option.key"
        :id="option.key"
        v-model="entitiesOrigin"
        class="re-checkbox--dark"
        :value="option.key"
      >
        {{ option.name }}
      </ReCheckbox>
    </div>
    <div class="content">
      <text-spans
        v-for="origin in entitiesOrigin" :key="origin"
        :dataset="dataset" 
        :record="record"
        :entities="record[origin].entities"
        :agent="record[origin].agent"
        @updateRecordEntities="updateRecordEntities"     
          />
    </div>
    <div v-if="annotationEnabled" class="content__actions-buttons">
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
  data: function () {
    return {
      selectionStart: undefined,
      selectionEnd: undefined,
      entitiesOptions: [ {key: 'annotation', name: 'Annotation'}, {key: 'prediction', name: 'Prediction'}],
      visibleEntities: ['annotation'],
    };
  },
  computed: {
    annotationEnabled() {
      return this.dataset.viewSettings.viewMode === "annotate";
    },
    entitiesOrigin: {
      get () {
        return this.visibleEntities;     
      },
      set (val) {
        if (!this.annotationEnabled) {
          this.visibleEntities = val  
        }          
      }
    }
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
      discard: "entities/datasets/discardAnnotations",
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
.record {
  padding: 44px 20px 20px 20px;
  display: block;
  margin-bottom: 0; // white-space: pre-line;
  @include font-size(16px);
  line-height: 1.6em;
  .list__item--annotation-mode & {
    padding-left: 65px;
  }
}
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
  &__toggle {
    .re-checkbox--dark {
      line-height: 20px;
      align-items: center;
      margin-right: 2em;
      ::v-deep {
        .checkbox-label {
          height: auto;
          margin-right: 1em;
        }
      }
    }
  }
}
</style>
