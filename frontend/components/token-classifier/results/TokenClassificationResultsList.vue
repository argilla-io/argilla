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
          :numberOfRecords="numberOfRecords"
          @on-search-entity="(value) => (searchQuery = value)"
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
import {
  TokenClassificationDataset,
  TokenClassificationDataset as TokenClassificationModel,
} from "../../../models/TokenClassification";
import RuleDefinitionToken from "../labelling-rules/RuleDefinitionToken.component.vue";
import { getDatasetModelPrimaryKey } from "../../../models/Dataset";
import {
  formatDatasetIdForTokenEntityModel,
  TokenEntity,
} from "../../../models/token-classification/TokenEntity.modelTokenClassification";
import {
  getTokenAnnotationModelPrimaryKey,
  TokenAnnotation as TokenAnnotationModel,
} from "../../../models/token-classification/TokenAnnotation.modelTokenClassification";

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
      searchQuery: "",
    };
  },
  components: {
    RuleDefinitionToken,
  },
  async beforeMount() {
    this.rulesHaveBeenFetched = false;
    const { name } = this.dataset;

    const rulesMetrics = await this.getRulesMetricsByQueryText(
      name,
      this.queryText
    );

    const rules = await this.fetchTokenClassificationRules(name);

    rules?.forEach((rule) => {
      this.insertOrUpdateDataInRuleModel(rule, rulesMetrics);
    });

    await this.addAnnotationsToRecordsByQuery(name, this.queryText);

    this.insertOrUpdateEntityInTokenEntityModel();
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
      return this.viewMode === "labelling-rules";
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
        TokenClassificationModel.find(this.datasetPrimaryKey).query.text || ""
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
      return TokenEntity.query()
        .where(
          "dataset_id",
          formatDatasetIdForTokenEntityModel(this.datasetPrimaryKey)
        )
        .where("text", (value) =>
          this.isStringIncludeSubstring(value, this.searchQuery)
        )
        .orderBy("text")
        .get();
    },
    records() {
      return TokenClassificationDataset.query()
        .whereId(this.datasetPrimaryKey)
        .with("token_records")
        .first().token_records;
    },
    recordsIds() {
      return this.records.map((record) => record.id);
    },
    numberOfRecords() {
      return (
        this.rule.rule_metrics?.coverage *
          this.rule.rule_metrics?.total_records || null
      );
    },
  },
  methods: {
    async getRulesMetricsByQueryText(name, query) {
      let rulesMetrics = null;

      if (query) {
        rulesMetrics = await this.fetchRuleMetricsByQueryText(name, query);
      }
      return rulesMetrics;
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
    async fetchRuleMetricsByQueryText(name, query) {
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
    async addAnnotationsToRecordsByQuery(name, query) {
      const data = query
        ? await this.fetchRecordsAnnotationByQueryText(name, query)
        : null;

      if (data) {
        this.insertOrUpdateAnnotationsInTokenAnnotation(data, query);
      }
    },
    async fetchRecordsAnnotationByQueryText(name, query) {
      try {
        const { data, status } = await this.$axios.post(
          `/datasets/${name}/TokenClassification/labeling/rules/${query}/search`,
          {
            record_ids: this.recordsIds,
          }
        );
        if (status === 200) {
          return data;
        } else {
          throw new Error("Error fetching API records annotations");
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
          dataset_id: this.dataset.id,
          name: this.dataset.name,
          owner: this.dataset.owner,
        },
      });
    },
    insertOrUpdateEntityInTokenEntityModel() {
      const entities = [];

      this.dataset.entities.forEach(({ text, colorId }) => {
        const entity = {
          dataset_id: formatDatasetIdForTokenEntityModel(
            this.datasetPrimaryKey
          ),
          text: text,
          color_id: colorId,
          is_activate: false,
        };

        entities.push(entity);
      });

      TokenClassificationModel.insertOrUpdate({
        where: this.datasetPrimaryKey,
        data: {
          token_entities: entities,
        },
      });
    },
    insertOrUpdateAnnotationsInTokenAnnotation({ agent, records }, query) {
      const { owner, name } = this.dataset;

      records.forEach(({ id: record_id, entities }) => {
        const objToInitPrimaryKeys = {
          record_id,
          agent,
          owner,
          name,
        };

        const primaryKey =
          getTokenAnnotationModelPrimaryKey(objToInitPrimaryKeys);

        TokenAnnotationModel.insertOrUpdate({
          where: primaryKey,
          data: {
            record_id,
            entities,
            agent,
            query,
            owner,
            name,
          },
        });
      });
    },
    isStringIncludeSubstring(refString, substring) {
      return refString.toLowerCase().includes(substring.toLowerCase());
    },
  },
};
</script>
