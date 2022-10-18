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
  <results-list :dataset="dataset">
    <template slot="results-header">
      <!-- <rule-definition :dataset="dataset" v-if="isLabellingRules" /> -->
      <RuleDefinitionToken :datasetId="dataset.id" v-if="isLabellingRules">
      </RuleDefinitionToken>
    </template>
    <template slot="record" slot-scope="results">
      <record-token-classification
        :dataset="dataset"
        :record="results.record"
      />
    </template>
  </results-list>
</template>

<script>
import RuleModel from "../../../models/token-classification/Rule.modelTokenClassification";
import RuleDefinitionToken from "../labelling-rules/RuleDefinitionToken.component.vue";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  components: {
    RuleDefinitionToken,
  },
  async beforeMounted() {
    const { name } = this.dataset;

    //call computed rules
    const rules = await this.fetchTokenClassificationRules(name);

    rules.forEach((rule) => {
      this.fetchRuleMetricsByRuleAndInsertInDatabase(name, rule);
    });
  },
  computed: {
    isLabellingRules() {
      return this.dataset.viewSettings.viewMode === "labelling-rules";
    },
  },
  methods: {
    async fetchRuleMetricsByRuleAndInsertInDatabase(name, rule) {
      const rulesMetrics =
        await this.fetchTokenClassificationRulesMetricsByRule(name, rule.query);

      RuleModel.insertOrUpdate({
        data: {
          dataset_id: this.dataset.$id,
          ...rule,
          rule_metrics: rulesMetrics,
        },
      });
    },
    async fetchTokenClassificationRules(name) {
      try {
        const { data, status } = await this.$axios.get(
          `/datasets/${name}/TokenClassification/labeling/rules`
        );
        if (status === 200) {
          return data;
        } else {
          throw new Error("Error fetching API rules");
        }
      } catch (err) {
        console.log("Error: ", error);
      }
    },
    async fetchTokenClassificationRulesMetricsByRule(name, query) {
      try {
        const { data, status } = await this.$axios.get(
          `/datasets/${name}/TokenClassification/labeling/rules/${query}:summary`
        );
        if (status === 200) {
          return data;
        } else {
          throw new Error("Error fetching API rule metrics");
        }
      } catch (error) {
        console.log("Error: ", error);
      }
    },
  },
};
</script>
