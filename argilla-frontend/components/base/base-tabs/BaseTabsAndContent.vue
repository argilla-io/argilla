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
    <BaseTabs
      :tabs="tabs"
      :active-tab="currentTab"
      :tab-size="tabSize"
      @change-tab="getSelectedTab"
    />
    <transition name="fade" mode="out-in" appear>
      <slot :current-component="currentComponent" />
    </transition>
  </div>
</template>
<script>
export default {
  props: {
    tabs: {
      type: Array,
      required: true,
    },
    tabSize: {
      type: String,
    },
  },
  data() {
    return {
      currentTab: this.tabs[0],
    };
  },
  computed: {
    currentComponent() {
      return this.currentTab.component;
    },
  },
  watch: {
    currentTab() {
      this.$emit("onChanged", this.currentTab.id);
    },
  },
  methods: {
    getSelectedTab(id) {
      this.currentTab = this.tabs.find((tab) => tab.id === id);
    },
  },
  mounted() {
    this.$emit("onLoaded");

    this.$emit("onChanged", this.currentTab.id);
  },
};
</script>
