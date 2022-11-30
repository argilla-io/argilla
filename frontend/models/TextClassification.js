/*
 * coding=utf-8
 * Copyright 2021-present, the Recognai S.L. team.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {
  ObservationDataset,
  USER_DATA_METADATA_KEY,
  getDatasetModelPrimaryKey,
} from "./Dataset";
import { BaseRecord, BaseSearchQuery, BaseSearchResults } from "./Common";
import _ from "lodash";

class TextClassificationRecord extends BaseRecord {
  inputs;

  constructor({ inputs, explanation, multi_label, ...superData }) {
    super(superData);
    this.inputs = inputs;
    this.explanation = explanation;
    this.multi_label = multi_label;
  }

  recordTitle() {
    return this.inputs;
  }

  get predicted_as() {
    if (this.prediction === undefined) {
      return [];
    }
    let labels = this.prediction.labels;
    if (this.multi_label) {
      return labels.filter((l) => l.score > 0.5).map((l) => l.class);
    }
    return [this.prediction.labels[0].class];
  }

  get annotated_as() {
    if (this.annotation === undefined) {
      return [];
    }
    let labels = this.annotation.labels;
    if (this.multi_label) {
      return labels.map((l) => l.class);
    }
    return [this.annotation.labels[0].class];
  }

  get predicted() {
    if (
      !this.multi_label &&
      this.prediction &&
      this.predicted_as &&
      this.annotated_as
    ) {
      return this.predicted_as[0] === this.annotated_as[0] ? "ok" : "ko";
    }
    return undefined;
  }

  get clipboardText() {
    if (Object.keys(this.inputs).length > 1) {
      return Object.keys(this.inputs)
        .map(
          (key, index) =>
            `${key.toUpperCase()}\n${this.inputs[key]}${
              Object.keys(this.inputs).length === index + 1 ? "" : "\n\n"
            }`
        )
        .join("");
    } else {
      return Object.values(this.inputs);
    }
  }
}

class TextClassificationSearchQuery extends BaseSearchQuery {
  score;

  constructor(data) {
    const { score, confidence, uncovered_by_rules, ...superData } = data;
    super(superData);
    this.score = score;
    this.uncovered_by_rules = uncovered_by_rules;
    // TODO: remove backward compatibility
    if (confidence) {
      this.score = confidence;
    }
  }
}

class TextClassificationSearchResults extends BaseSearchResults {
  constructor({ total, records, aggregations }) {
    super({
      total,
      aggregations,
      records: (records || []).map(
        (record) => new TextClassificationRecord(record)
      ),
    });
  }
}

class TextClassificationDataset extends ObservationDataset {
  static entity = "text_classification";

  static fields() {
    return {
      ...super.fields(),
      settings: this.attr({}),
      _labels: this.attr([]),
      // Search fields
      query: this.attr({}, (data) => {
        return new TextClassificationSearchQuery(data);
      }),
      sort: this.attr([]),
      results: this.attr(
        {},
        (data) => new TextClassificationSearchResults(data)
      ),
      // Some kind of metrics fields
      globalResults: this.attr({}),
      // labeling rules fields
      isMultiLabel: this.boolean(false),
      rules: this.attr(null),
      rulesOveralMetrics: this.attr(null),
      perRuleQueryMetrics: this.attr(null),
      activeRule: this.attr(null),
      activeRuleMetrics: this.attr(null),
    };
  }

  static apiConfig = {
    save: false,
  };

  async initialize() {
    const settings = await this._getDatasetSettings();
    const { labels } = await this.fetchMetricSummary("dataset_labels");
    const entity = this.getTaskDatasetClass();
    const isMultiLabel = this.results.records.some((r) => r.multi_label);
    await entity.insertOrUpdate({
      where: this.id,
      data: [
        {
          owner: this.owner,
          name: this.name,
          _labels: labels,
          settings,
          isMultiLabel,
        },
      ],
    });
    if (!this.labelingRules) {
      await this.refreshRules();
    }
    return entity.find(getDatasetModelPrimaryKey(this));
  }

  async _getRule({ query }) {
    const { response } = await TextClassificationDataset.api().get(
      `/datasets/${this.task}/${this.name}/labeling/rules/${encodeURIComponent(
        query
      )}`,
      {
        // Ignore errors related to rule not found
        validateStatus: function (status) {
          return status === 404 || (status >= 200 && status < 300);
        },
      }
    );
    if (response.status === 404) {
      return undefined;
    }
    return response.data;
  }

  async _deleteRule({ query }) {
    const { response } = await TextClassificationDataset.api().delete(
      `/datasets/${this.task}/${this.name}/labeling/rules/${encodeURIComponent(
        query
      )}`
    );
    return response.data;
  }

  async _fetchAllRules() {
    const { response } = await TextClassificationDataset.api().get(
      `/datasets/${this.task}/${this.name}/labeling/rules`
    );
    return response.data;
  }

  async _fetchOveralMetrics(rulesMetrics) {
    if (!rulesMetrics.length) {
      // TODO: fix server error
      return {};
    }

    const { response } = await TextClassificationDataset.api().get(
      `/datasets/${this.task}/${this.name}/labeling/rules/metrics`
    );

    let overalMetrics = response.data;
    if (rulesMetrics) {
      overalMetrics = {
        ...response.data,
        ...rulesMetrics.reduce(
          (
            { precisionAverage, totalCorrects, totalIncorrects },
            { correct, incorrect, precision }
          ) => {
            return {
              precisionAverage: precisionAverage + (precision || 0),
              totalCorrects: totalCorrects + correct,
              totalIncorrects: totalIncorrects + incorrect,
            };
          },
          {
            precisionAverage: 0,
            totalCorrects: 0,
            totalIncorrects: 0,
          }
        ),
      };
      overalMetrics.precisionAverage =
        overalMetrics.totalCorrects /
        (overalMetrics.totalCorrects + overalMetrics.totalIncorrects);
    }

    return overalMetrics;
  }

  async _persistRule({ query, labels, description }) {
    let { response } = await TextClassificationDataset.api().post(
      `/datasets/${this.task}/${this.name}/labeling/rules`,
      { query, labels, description },
      {
        // Ignore errors related to rule not found
        validateStatus: function (status) {
          return status === 409 || (status >= 200 && status < 300);
        },
      }
    );
    if (response.status === 409) {
      const apiResult = await TextClassificationDataset.api().patch(
        `/datasets/${this.task}/${
          this.name
        }/labeling/rules/${encodeURIComponent(query)}`,
        { labels, description }
      );
      response = apiResult.response;
    }

    return response.data;
  }

  async _fetchRuleMetrics({ query, labels }) {
    var url = `/datasets/${this.task}/${
      this.name
    }/labeling/rules/${encodeURIComponent(query)}/metrics`;
    if (labels !== undefined) {
      const urlLabels = labels.map((label) => `label=${label}`);
      url += `?${urlLabels.join("&")}`;
    }
    const { response } = await TextClassificationDataset.api().get(url);

    const metrics = response.data;
    // Computed extra metrics
    metrics.records = Math.round(metrics.total_records * metrics.coverage);

    return metrics;
  }

  async refreshRulesMetrics() {
    if (this.rules === null) {
      // TODO: maybe we can automatically load rules before metrics
      throw Error("No rules info found");
    }

    const responses = await Promise.all(
      this.rules.map((rule) => {
        return this._fetchRuleMetrics(rule);
      })
    );

    var perRuleQueryMetrics = {};
    responses.forEach((response, idx) => {
      perRuleQueryMetrics[this.rules[idx].query] = response;
    });

    const overalMetrics = await this._fetchOveralMetrics(responses);

    return await TextClassificationDataset.insertOrUpdate({
      where: this.id,
      data: {
        owner: this.owner,
        name: this.name,
        perRuleQueryMetrics,
        rulesOveralMetrics: overalMetrics,
      },
    });
  }

  async refreshRules() {
    const rules = await this._fetchAllRules();
    await TextClassificationDataset.insertOrUpdate({
      data: {
        owner: this.owner,
        name: this.name,
        rules,
      },
    });
  }

  get labels() {
    const predefinedLabels =
      this.settings.label_schema && this.settings.label_schema.labels;

    if (predefinedLabels) {
      return predefinedLabels.map((l) => l.id).sort();
    }
    const { labels } = (this.metadata || {})[USER_DATA_METADATA_KEY] || {};
    const aggregations = this.globalResults.aggregations;
    const label2str = (label) => label.class;
    const recordsLabels = this.results.records.flatMap((record) => {
      return []
        .concat(
          record.annotation ? record.annotation.labels.map(label2str) : []
        )
        .concat(
          record.prediction ? record.prediction.labels.map(label2str) : []
        );
    });

    const uniqueLabels = [
      ...new Set(
        (labels || [])
          .filter((l) => l && l.trim())
          .concat(this._labels || [])
          .concat(recordsLabels)
          .concat(Object.keys(aggregations.annotated_as))
          .concat(Object.keys(aggregations.predicted_as))
      ),
    ];
    uniqueLabels.sort();
    return uniqueLabels;
  }

  get labelingRulesMetrics() {
    return this.perRuleQueryMetrics === null
      ? undefined
      : this.perRuleQueryMetrics;
  }

  get labelingRules() {
    return this.rules === null ? undefined : this.rules;
  }

  get labelingRulesOveralMetrics() {
    return this.rulesOveralMetrics === null
      ? undefined
      : this.rulesOveralMetrics;
  }

  getCurrentLabelingRule() {
    return this.activeRule === null ? undefined : this.activeRule;
  }

  getCurrentLabelingRuleMetrics() {
    return this.activeRuleMetrics === null ? undefined : this.activeRuleMetrics;
  }

  async setCurrentLabelingRule({ query, labels }) {
    if (
      this.currentLabelingRule &&
      query === this.currentLabelingRule.query &&
      _.isEqual(_.sortBy(labels), _.sortBy(this.currentLabelingRule.labels))
    ) {
      return;
    }

    let rule = this.findRuleByQuery(query, labels);
    let ruleMetrics = this.getMetricsByRule(rule);

    await TextClassificationDataset.insertOrUpdate({
      data: {
        owner: this.owner,
        name: this.name,
        activeRule: rule || {
          query,
          labels,
          description: query,
        },
        activeRuleMetrics:
          ruleMetrics || (await this._fetchRuleMetrics({ query, labels })),
      },
    });
  }

  async storeLabelingRule(activeRule) {
    let rule = await this._persistRule(activeRule);

    const rules = this.rules.filter((rule) => rule.query !== activeRule.query);
    const perRuleQueryMetrics = {
      ...this.perRuleQueryMetrics,
      [activeRule.query]: this.activeRuleMetrics,
    };
    if (rule === undefined) {
      rule = await this._getRule({ query: activeRule.query });
    }

    rules.push(rule);

    const overalMetrics = await this._fetchOveralMetrics(
      Object.values(perRuleQueryMetrics)
    );

    await TextClassificationDataset.insertOrUpdate({
      data: {
        owner: this.owner,
        name: this.name,
        rules,
        activeRule,
        perRuleQueryMetrics,
        rulesOveralMetrics: overalMetrics,
      },
    });
  }

  async deleteLabelingRule({ query }) {
    await this._deleteRule({ query });

    const currentRule = this.getCurrentLabelingRule();
    if (query === (currentRule || {}).query) {
      await this.clearCurrentLabelingRule();
    }

    const rules = this.rules.filter((r) => r.query !== query);
    const perRuleQueryMetrics = { ...this.perRuleQueryMetrics };
    delete perRuleQueryMetrics[query];
    const overalMetrics = await this._fetchOveralMetrics(
      Object.values(perRuleQueryMetrics)
    );

    await TextClassificationDataset.insertOrUpdate({
      data: {
        owner: this.owner,
        name: this.name,
        rules,
        perRuleQueryMetrics,
        rulesOveralMetrics: overalMetrics,
      },
    });
  }

  async clearCurrentLabelingRule() {
    await TextClassificationDataset.insertOrUpdate({
      data: {
        owner: this.owner,
        name: this.name,
        activeRule: null,
        activeRuleMetrics: null,
      },
    });
  }

  findRuleByQuery(query, labels = undefined) {
    for (let rule of this.labelingRules || []) {
      const labelsAreEqual = _.isEqual(_.sortBy(rule.labels), _.sortBy(labels));
      if (rule.query === query && (!labels || labelsAreEqual)) {
        return rule;
      }
    }
  }

  getMetricsByRule(rule) {
    if (rule) return (this.labelingRulesMetrics || {})[rule.query];
  }
}

ObservationDataset.registerTaskDataset(
  "TextClassification",
  TextClassificationDataset
);

export {
  TextClassificationDataset,
  TextClassificationRecord,
  TextClassificationSearchResults,
  TextClassificationSearchQuery,
};
