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
  <div class="metadata">
    <div class="metadata__container">
      <div v-for="(item, index) in formatSortedMetadataItems" :key="index">
        <div class="metadata__blocks">
          <base-checkbox
            :id="item[0]"
            v-model="selectedMetadata"
            class="re-checkbox--dark"
            :value="item[0]"
          >
            <div class="metadata__key">
              {{ item[0] }}
              <div class="metadata__value">
                {{ item[1] }}
              </div>
            </div>
          </base-checkbox>
        </div>
      </div>
    </div>
    <div class="metadata__buttons">
      <base-button class="primary outline" @click="$emit('cancel')">
        Cancel
      </base-button>
      <base-button class="primary" @click="applySelectedFilters()">
        Filter
      </base-button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    metadataItems: {
      type: Object,
      required: true,
    },
    appliedFilters: {
      type: Object,
      default: () => {},
    },
    title: {
      type: [Object, String],
      required: true,
    },
  },
  data: () => ({
    selectedMetadata: [],
  }),
  computed: {
    normalizedMetadataItems() {
      return Object.keys(this.metadataItems).reduce(
        (r, k) => (
          (r[k] =
            Array.isArray(this.metadataItems[k]) &&
            this.metadataItems[k].length > 1
              ? this.metadataItems[k]
              : String(this.metadataItems[k])),
          r
        ),
        {}
      );
    },
    sortedMetadataItems() {
      return Object.keys(this.normalizedMetadataItems)
        .sort()
        .reduce((r, k) => ((r[k] = this.normalizedMetadataItems[k]), r), {});
    },
    formatSortedMetadataItems() {
      return Object.entries(this.sortedMetadataItems);
    },
  },
  mounted() {
    if (this.appliedFilters) {
      Object.keys(this.appliedFilters).map((key) => {
        const equalLength =
          this.appliedFilters[key].length ===
          this.normalizedMetadataItems[key].length;
        if (
          Array.isArray(this.normalizedMetadataItems[key]) && equalLength
            ? this.appliedFilters[key].every((f) =>
                this.normalizedMetadataItems[key].includes(f)
              )
            : this.appliedFilters[key].includes(
                this.normalizedMetadataItems[key]
              )
        ) {
          this.selectedMetadata.push(key);
        }
      });
    }
  },
  methods: {
    applySelectedFilters() {
      const filters = Object.keys(this.appliedFilters || {}).reduce(
        (r, k) => (
          (r[k] = Array.isArray(this.appliedFilters[k])
            ? this.appliedFilters[k].length ===
                this.normalizedMetadataItems[k].length &&
              this.appliedFilters[k].every((f) =>
                this.normalizedMetadataItems[k].includes(f)
              )
              ? []
              : this.appliedFilters[k]
            : []),
          r
        ),
        {}
      );

      this.selectedMetadata.map((key) => {
        filters[key] = this.normalizedMetadataItems[key];
      });

      this.$emit("metafilterApply", filters);
    },
  },
};
</script>

<style lang="scss" scoped>
.metadata {
  position: relative;
  max-width: 500px;
  margin: auto;
  pointer-events: all;
  &__container {
    max-height: 50vh;
    overflow-y: auto;
    margin-right: -1em;
    padding-right: 1em;
    @extend %hide-scrollbar;
  }
  &__blocks {
    display: flex;
    align-items: center;
    .re-checkbox--dark {
      width: 100%;
      display: flex;
      align-items: center;
      margin-right: 0;
    }
    :deep(.checkbox-label) {
      height: auto !important;
    }
  }
  &__block {
    padding: 1em 0;
    margin-right: 0.5em;
    color: $font-dark;
    font-weight: 600;
    &__item {
      min-width: 200px;
      max-width: 300px;
      text-align: left;
      white-space: pre-line;
      color: $font-medium;
      font-weight: normal;
      line-height: 1em;
      word-break: break-word;
      hyphens: auto;
    }
  }
  &__key {
    display: block;
    margin-bottom: 0.5em;
  }
  &__value {
    display: block;
    margin-bottom: 0.5em;
  }
  &__buttons {
    display: block;
    text-align: right;
    margin-top: 2em;
    display: flex;
    .button {
      width: 100%;
      justify-content: center;
      &:last-of-type {
        margin-left: $base-space;
      }
    }
  }
}
</style>
