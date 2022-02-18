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
  <div class="app__content">
    <div :class="['grid', annotationEnabled ? 'grid--editable' : '']">
      <Results :dataset="dataset" />
    </div>
  </div>
</template>
<script>
import "assets/icons/copy";
import { mapActions } from "vuex";
import { currentWorkspace } from "@/models/Workspace";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  computed: {
    annotationEnabled() {
      return this.dataset.viewSettings.viewMode === "annotate";
    },
    workspace() {
      return currentWorkspace(this.$route);
    },
  },
  methods: {
    ...mapActions({
      fetchDataset: "entities/datasets/fetchByName",
    }),
  },
};
</script>
<style lang="scss" scoped>
.app {
  display: flex;
  &__content {
    width: 100%;
  }
}
.container {
  @extend %container;
  padding-top: 0;
  padding-bottom: 0;
  margin-left: 0;
  &--intro {
    padding-top: 2em;
    margin-bottom: 1.5em;
    &:after {
      border-bottom: 1px solid $line-light-color;
      content: "";
      margin-bottom: 1.5em;
      position: absolute;
      left: 0;
      right: 0;
    }
  }
}

.grid {
  position: relative;
  margin: 0;
}
</style>
