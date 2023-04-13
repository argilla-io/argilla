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
  <BaseSidebarProgress
    v-if="annotationsProgress"
    :total="total"
    :validated="validated"
    :discarded="discarded"
  />
</template>

<script>
import { AnnotationProgress } from "@/models/AnnotationProgress";
export default {
  props: {
    datasetName: {
      type: String,
      required: true,
    },
  },
  computed: {
    total() {
      return this.annotationsProgress.total;
    },
    validated() {
      return this.annotationsProgress.validated;
    },
    discarded() {
      return this.annotationsProgress.discarded;
    },
    annotationsProgress() {
      return AnnotationProgress.find(this.datasetName);
    },
  },
};
</script>
<style lang="scss" scoped></style>
