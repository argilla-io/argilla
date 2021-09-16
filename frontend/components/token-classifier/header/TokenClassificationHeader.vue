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
    <header-title title="Token Classification" v-if="dataset.results.records" :dataset="dataset" />
    <filters-area :dataset="dataset" />
    <entities-header :dataset="dataset" />
    <global-actions :dataset="dataset">
      <validate-discard-action
        :dataset="dataset"
        @discard-records="onDiscard"
        @validate-records="onValidate"
      >
      </validate-discard-action>
      <create-new-action @new-label="onNewLabel" />
    </global-actions>
  </div>
</template>
<script>
import { mapActions } from "vuex";
export default {
  props: {
    dataset: {
      required: true,
      type: Object,
    },
  },
  computed: {
    showAnnotationMode() {
      return this.dataset.viewSettings.annotationEnabled;
    },
  },

  methods: {
    ...mapActions({
      discard: "entities/datasets/discardAnnotations",
      validate: "entities/datasets/validateAnnotations",
    }),

    async onDiscard(records) {
      await this.discard({
        dataset: this.dataset,
        records: records,
      });
    },
    async onValidate(records) {
      await this.validate({
        dataset: this.dataset,
        records: records.map((record) => ({
          ...record,
          annotation: {
            ...(record.annotation || record.prediction),
            agent: this.$auth.user,
          },
        })),
      });
    },
    async onNewLabel(label) {
      await this.dataset.$dispatch("setEntities", {
        dataset: this.dataset,
        entities: [
          ...new Set([...this.dataset.entities.map((ent) => ent.text), label]),
        ],
      });
    },
  },
};
</script>
