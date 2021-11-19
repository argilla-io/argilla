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
  <div class="header__filters">
    <header-title
      v-if="dataset.results.records"
      title="Text2Text"
      :dataset="dataset"
    />
    <filters-area :dataset="dataset" />
    <global-actions :dataset="dataset">
      <validate-discard-action
        :dataset="dataset"
        @discard-records="onDiscard"
        @validate-records="onValidate"
      >
      </validate-discard-action>
    </global-actions>
  </div>
</template>
<script>
import { mapActions } from "vuex";
import { getUsername } from "@/models/User";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  methods: {
    ...mapActions({
      discardAnnotations: "entities/datasets/discardAnnotations",
      validateAnnotations: "entities/datasets/validateAnnotations",
    }),
    async onDiscard(records) {
      await this.discardAnnotations({
        dataset: this.dataset,
        records: records,
      });
    },
    async onValidate(records) {
      await this.validateAnnotations({
        dataset: this.dataset,
        agent: getUsername(this.$auth),
        records: records,
      });
    },
  },
};
</script>
