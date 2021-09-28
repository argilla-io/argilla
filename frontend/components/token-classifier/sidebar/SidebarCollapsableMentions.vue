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
    <div
      v-for="(item, index) in Object.entries(object[k]).slice(0, limit)"
      :key="index"
      class="info"
    >
      <label>{{ item[0] }}</label>
      <span class="records-number">
        <strong>{{ item[1] | formatNumber }}</strong>
      </span>
    </div>
    <a
      v-if="limit !== 0 && Object.entries(object[k]).length > 3"
      class="sidebar__view-more"
      href="#"
      @click.prevent="$emit('limit', k)"
      >{{ limit === 3 ? `view more` : `view less` }}</a
    >
  </div>
</template>
<script>
export default {
  props: {
    limit: {
      type: Number,
      required: true,
    },
    object: {
      type: Object,
      required: true,
    },
    k: {
      type: String,
      required: true,
    },
  },
};
</script>
<style scoped lang="scss">
.sidebar {
  &__view-more {
    color: $font-secondary;
    text-decoration: none;
    outline: none;
    margin-bottom: 1.5em;
    display: inline-block;
  }
}
.info {
  color: $font-secondary-dark;
  position: relative;
  display: flex;
  margin-bottom: 0.7em;
}
.records-number {
  margin-right: 0;
  margin-left: auto;
  font-weight: bold;
}
</style>
