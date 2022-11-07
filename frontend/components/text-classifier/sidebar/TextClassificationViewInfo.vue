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
  <div class="help">
    <lazy-base-modal
      modal-class="modal-secondary"
      modal-position="modal-center"
      :modal-custom="true"
      :prevent-body-scroll="true"
      :modal-visible="visibleViewInfo"
      @close-modal="closeModal"
    >
      <div class="help__panel">
        <p class="help__panel__title">
          This dataset contains token attributions. What do highlight colors
          mean?
        </p>
        <p>
          Argilla enables you to register token attributions as part of the
          dataset records. For getting token attributions, you can use methods
          such as Integrated Gradients or SHAP. These methods try to provide a
          mechanism to interpret model predictions.
        </p>
        <p>The attributions work as follows:</p>
        <p>
          [0,1] <strong>Positive attributions</strong> (in blue) reflect those
          tokens that are making the model predict the specific predicted label.
        </p>
        <p>
          [-1, 0] <strong>Negative attributions</strong> (in red) reflect those
          tokens that can influence the model to predict a label other than the
          specific predicted label.
        </p>
      </div>
      <base-button class="primary" @click="closeModal"> Close </base-button>
    </lazy-base-modal>
  </div>
</template>

<script>
import "assets/icons/support";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  computed: {
    visibleViewInfo() {
      return this.dataset?.viewSettings.visibleViewInfo;
    },
  },
  methods: {
    async closeModal() {
      await this.dataset.viewSettings.openViewInfo(false);
    },
  },
};
</script>

<style lang="scss" scoped>
.help {
  clear: both;
  margin-top: 0em;
  margin-bottom: 1em;
  padding-left: 4em;
  @extend %collapsable-if-metrics !optional;
  &__panel {
    color: $black-54;
    border-radius: 1px;
    position: relative;
    margin-bottom: $base-space * 4;
    &__title {
      @include font-size(16px);
      color: $black-54;
      font-weight: 600;
      margin-top: 0;
    }
    ul,
    p {
      @include font-size(13px);
    }
    ul {
      padding-left: 1.5em;
      margin-bottom: 1.5em;
    }
  }
}
</style>
