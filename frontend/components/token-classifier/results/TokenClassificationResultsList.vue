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
    <template slot="results-header" v-if="isLabellingRules">
      <transition name="fade" mode="out-in" appear>
        <RuleDefinitionToken
          :rule="rule"
          :queryText="queryText"
          :entities="entities"
        />
      </transition>
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
import {
  Rule as RuleModel,
  getRuleModelPrimaryKey,
} from "../../../models/token-classification/Rule.modelTokenClassification";
import { TokenClassificationDataset } from "../../../models/TokenClassification";
import RuleDefinitionToken from "../labelling-rules/RuleDefinitionToken.component.vue";
import {
  getDatasetModelPrimaryKey,
  ObservationDataset,
} from "../../../models/Dataset";
import { SearchRulesRecord } from "../../../models/token-classification/SearchRulesRecord.modelTokenClassification";
import {
  TokenEntity,
  formatDatasetIdForTokenEntityModel,
} from "../../../models/token-classification/TokenEntity.modelTokenClassification";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      rulesHaveBeenFetched: false,
    };
  },
  components: {
    RuleDefinitionToken,
  },
  async beforeMount() {
    this.rulesHaveBeenFetched = false;
    const { name } = this.dataset;
    const rules = await this.fetchTokenClassificationRules(name);

    rules.forEach(async (rule) => {
      await this.initRuleModelTable(name, rule);
      await this.initSearchRuleRecordsTable(name, rule);
    });
    this.rulesHaveBeenFetched = true;
  },
  computed: {
    owner() {
      return this.dataset.owner;
    },
    name() {
      return this.dataset.name;
    },
    viewMode() {
      return this.dataset.viewSettings.viewMode;
    },
    isLabellingRules() {
      return this.viewMode === "labelling-rules" && this.rulesHaveBeenFetched;
    },
    datasetPrimaryKey() {
      const paramsToGetDatasetPrimaryKey = {
        name: this.name,
        owner: this.owner,
      };
      return getDatasetModelPrimaryKey(paramsToGetDatasetPrimaryKey);
    },
    queryText() {
      return (
        TokenClassificationDataset.find(this.datasetPrimaryKey).query.text || ""
      );
    },
    rulePrimaryKey() {
      const paramsToGetRulePrimaryKey = {
        query: this.queryText,
        name: this.name,
        owner: this.owner,
      };
      return getRuleModelPrimaryKey(paramsToGetRulePrimaryKey);
    },
    rule() {
      return (
        RuleModel.query()
          .with("rule_metrics")
          .whereId(this.rulePrimaryKey)
          .first() || {}
      );
    },
    entities() {
      return (
        this.datasetPrimaryKey,
        TokenEntity.query()
          .where(
            "dataset_id",
            formatDatasetIdForTokenEntityModel(this.datasetPrimaryKey)
          )
          .get()
      );
    },
  },
  methods: {
    async initRuleModelTable(name, rule) {
      const rulesMetrics = await this.fetchRuleMetricsByRule(name, rule);
      this.insertOrUpdateDataInRuleModel(rule, rulesMetrics);
    },
    async initSearchRuleRecordsTable(name, rule) {
      const searchRulesRecords =
        await this.fetchTokenClassificationSearchRuleRecords(name, rule.query);

      this.insertOrUpdateEntityInTokenEntityModel();
    },
    async fetchRuleMetricsByRule(name, rule) {
      return await this.fetchTokenClassificationRulesMetricsByRule(
        name,
        rule.query
      );
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
      } catch (error) {
        console.log("Error: ", error);
      }
    },
    async fetchTokenClassificationRulesMetricsByRule(name, query) {
      try {
        const { data, status } = await this.$axios.get(
          `/datasets/${name}/TokenClassification/labeling/rules/${query}/summary`
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
    async fetchTokenClassificationSearchRuleRecords(name, query) {
      try {
        const { data, status } = await this.$axios.get(
          `/datasets/${name}/TokenClassification/labeling/rules/${query}/search`
        );
        if (status === 200) {
          return data;
        } else {
          throw new Error("Error fetching API rule records");
        }
      } catch (error) {
        console.log("Error: ", error);
      }
    },
    insertOrUpdateDataInRuleModel(rule, rulesMetrics) {
      RuleModel.insertOrUpdate({
        data: {
          ...rule,
          rule_metrics: rulesMetrics,
          dataset_id: this.dataset.$id,
          name: this.dataset.name,
          owner: this.dataset.owner,
        },
      });
    },
    insertOrUpdateEntityInTokenEntityModel() {
      this.dataset.entities.forEach(({ text, colorId }) => {
        TokenEntity.insertOrUpdate({
          data: {
            dataset_id: formatDatasetIdForTokenEntityModel(
              this.datasetPrimaryKey
            ),
            text: text,
            color_id: colorId,
          },
        });
      });
    },
  },
};
</script>
