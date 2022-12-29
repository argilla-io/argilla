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
  <base-loading v-if="$fetchState.pending" />
  <div
    :class="[
      'app',
      annotationEnabled ? '--annotation' : '',
      areMetricsVisible ? '--metrics' : '',
    ]"
    v-else
  >
    <app-header
      :dataset="dataset"
      :breadcrumbs="breadcrumbs"
      :enableSimilaritySearch="isReferenceRecord"
      @search-records="searchRecords"
    >
      <task-sidebar v-if="dataset" :dataset="dataset" />
    </app-header>
    <error
      v-if="$fetchState.error"
      link="/datasets"
      :where="datasetName"
      :error="$fetchState.error"
    ></error>
    <task-search v-else :dataset="dataset" @search-records="searchRecords" />
  </div>
</template>

<script>
import _ from "lodash";
import { mapActions, mapGetters } from "vuex";
import { currentWorkspace } from "@/models/Workspace";
import { Vector as VectorModel } from "@/models/Vector";
import { Base64 } from "js-base64";
import { RefRecord as RefRecordModel } from "@/models/RefRecord";

export default {
  layout: "app",
  async fetch() {
    // 1. Clean models before fetching data. Remaining model info could affect the generated query
    await this.cleanModels();
    // 2. Fetch the record data and initialize the corresponding data models
    await this.fetchByName(this.datasetName);
    // 3. Fetch vector info from query param and setup the active vector if needed
    await this.activateVectorAndRecorByUrlQueryParams();
    // 4. If we have a vector filter, apply a search
    if (this.referenceRecordId) {
      await this.searchRecords({ query: this.dataset.query });
      await this.disablePagination(true);
    }
  },
  computed: {
    ...mapGetters({
      findByName: "entities/datasets/findByName",
    }),
    breadcrumbs() {
      return [
        { link: { path: "/datasets" }, name: "Datasets" },
        {
          link: { path: `/datasets?workspace=${this.workspace}` },
          name: this.workspace,
        },
        {
          link: this.$route.fullPath,
          name: this.dataset ? this.dataset.name : undefined,
        },
      ];
    },
    dataset() {
      // This computed data makes that store updates could be shown here
      try {
        return this.findByName(this.datasetName);
      } catch {
        return null;
      }
    },
    isDataset() {
      return !_.isNil(this.dataset);
    },
    isAnyReferenceRecord() {
      return VectorModel.all().length;
    },
    referenceRecordId() {
      return VectorModel.query().where("is_active", true).first();
    },
    datasetName() {
      return this.$route.params.dataset;
    },
    workspace() {
      return currentWorkspace(this.$route);
    },
    areMetricsVisible() {
      return this.dataset && this.dataset.viewSettings.visibleMetrics;
    },
    annotationEnabled() {
      return this.dataset && this.dataset.viewSettings.viewMode === "annotate";
    },
    isReferenceRecord() {
      const value = VectorModel.query().where("is_active", true).first();
      return !!value;
    },
  },
  destroyed() {},
  methods: {
    ...mapActions({
      fetchByName: "entities/datasets/fetchByName",
      search: "entities/datasets/search",
    }),
    async searchRecords({ query, sort, vector, recordId }) {
      if (vector || "vector" in query) {
        await this.syncRecordVectorInfo(vector, recordId);
      }
      await this.search({
        dataset: this.dataset,
        query,
        sort,
      });
    },
    async cleanModels() {
      await this.deleteAllVectorData();
      await this.deleteAllRecordReferenceData();
    },

    async deleteAllVectorData() {
      VectorModel.deleteAll();
    },

    async deleteAllRecordReferenceData() {
      await RefRecordModel.deleteAll();
    },

    disableCurrentVectorModel() {
      const vector = this.referenceRecordId;
      if (vector) {
        VectorModel.update({
          where: (v) => vector.record_id === v.record_id,
          data: { is_active: false },
        });
      }
    },
    async syncRecordVectorInfo(vector, recordId) {
      this.disableCurrentVectorModel();
      if (!vector) {
        // Update url query params
        this.updateUrlParamsWithVectorInfo(null);
        await this.disablePagination(false);
      } else {
        const { vectorId } = vector;
        // 1. Fetch record reference data
        await this.fetchRecordReferenceAndInsertIntoTheRefRecordModel(recordId);
        // 2. Set active vector model row to current one
        const vectorData = await VectorModel.update({
          where: vectorId,
          data: { is_active: true },
        });
        // 3. Update url query params
        this.updateUrlParamsWithVectorInfo(vectorData);
        // 4. Disable pagination
        await this.disablePagination(true);
      }
    },
    async activateVectorAndRecorByUrlQueryParams() {
      let vectorId = this.$route.query.vectorId;
      if (vectorId) {
        vectorId = JSON.parse(Base64.decode(vectorId));
        const { vector_name, record_id } = vectorId;
        await this.fetchRecordReferenceAndInsertIntoTheRefRecordModel(
          record_id
        );
        await VectorModel.update({
          where: (v) =>
            v.vector_name === vector_name &&
            v.dataset_id === this.dataset.id.join(".") &&
            v.record_id === record_id,
          data: {
            vector_name,
            is_active: true,
          },
        });
      }
    },
    updateUrlParamsWithVectorInfo(vectorData) {
      let vectorId = null;
      if (vectorData) {
        const { vector_name, record_id } = vectorData;
        vectorId = { vector_name, record_id };
        vectorId = Base64.encodeURI(JSON.stringify(vectorId));
      }
      this.$router.push({
        query: {
          ...this.$route.query,
          vectorId,
        },
      });
    },

    async fetchAndStoreReferenceRecord(recordId) {
      const { data: responseRecord } = await this.$axios.get(
        `/datasets/${this.dataset.name}/records/${recordId}`
      );

      await RefRecordModel.insertOrUpdate({
        data: {
          dataset_id: this.dataset.id.join("."),
          task: this.dataset.task,
          record_id: recordId,
          record_data: responseRecord,
        },
      });
      return responseRecord;
    },
    async upstertRecordReferenceVectors({ vectors, id }) {
      const vectorsByToInsertInModel = Object.entries(vectors).map(
        ([vectorName, { value: vectorValues }]) => {
          return {
            dataset_id: this.dataset.id.join("."),
            record_id: id,
            vector_name: vectorName,
            vector_values: vectorValues,
          };
        }
      );

      await VectorModel.insertOrUpdate({
        data: vectorsByToInsertInModel,
      });
    },
    async fetchRecordReferenceAndInsertIntoTheRefRecordModel(recordId) {
      try {
        const recordReference = await this.fetchAndStoreReferenceRecord(
          recordId
        );
        await this.upstertRecordReferenceVectors(recordReference);
      } catch (err) {
        console.warn(
          "Error on fetchRecordReferenceAndInsertIntoTheRefRecordModel",
          err
        );
      }
    },
    async disablePagination(value) {
      await this.dataset.viewSettings.disablePagination(value);
    }
  },
};
</script>

<style lang="scss" scoped></style>
