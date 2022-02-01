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
    <div
      ref="list"
      :class="showFullRecord ? 'record__expanded' : 'record__collapsed'"
    >
      <div class="content">
        <record-token-classification-annotation
          :dataset="dataset"
          :record="record"
          v-if="annotationEnabled"
        />
        <record-token-classification-exploration
          :dataset="dataset"
          :record="record"
          v-else
        />
      </div>
      <a
        href="#"
        v-if="scrollHeight >= visibleRecordHeight"
        class="record__button"
        @click.prevent="showFullRecord = !showFullRecord"
        >{{ !showFullRecord ? "Show full record" : "Show less" }}
      </a>
    </div>
  </div>
</template>

<script>
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
  data: () => ({
    showFullRecord: false,
    scrollHeight: undefined,
  }),
  updated() {
    this.calculateScrollHeight();
  },
  mounted() {
    this.calculateScrollHeight();
  },
  computed: {
    annotationEnabled() {
      return this.dataset.viewSettings.viewMode === "annotate";
    },
    visibleRecordHeight() {
      return this.$mq === "lg" ? 700 : 400;
    },
  },
  methods: {
    calculateScrollHeight() {
      if (this.$refs.list) {
        const padding = 2;
        this.scrollHeight = this.$refs.list.clientHeight + padding;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  padding: 52px 20px 20px 65px;
  display: block;
  margin-bottom: 0;
  @include font-size(18px);
  line-height: 34px;
  &__collapsed {
    .content {
      max-height: 400px;
      overflow: hidden;
      @include media(">xxl") {
        max-height: 700px;
      }
    }
  }
  &__button {
    display: inline-block;
    border-radius: 5px;
    padding: 0.5em;
    transition: all 0.2s ease;
    @include font-size(14px);
    font-weight: 400;
    background: none;
    margin-top: 1.5em;
    margin-bottom: 1em;
    font-weight: 600;
    text-decoration: none;
    line-height: 1;
    outline: none;
    &:hover {
      transition: all 0.2s ease;
      background: palette(grey, bg);
    }
  }
}
.content {
  position: relative;
  white-space: pre-wrap;
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
