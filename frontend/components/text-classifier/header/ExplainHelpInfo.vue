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
    <div
      v-if="!showHelpPanel"
      class="help__button"
      @click="showHelpPanel = true"
    >
      <svgicon name="support" width="22" height="22" color="#F38959"></svgicon>
      Help
    </div>
    <div v-if="showHelpPanel" class="help__panel">
      <div class="help__panel__button" @click="showHelpPanel = false">
        Close
      </div>
      <p class="help__panel__title">
        This dataset contains token attributions. What do highlight colors mean?
      </p>
      <p>
        Rubrix enables you to register token attributions as part of the dataset
        records. For getting token attributions, you can use methods such as
        Integrated Gradients or SHAP. These methods try to provide a mechanism
        to interpret model predictions.
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
  </div>
</template>

<script>
import "assets/icons/support";
export default {
  data: () => ({
    showHelpPanel: false,
  }),
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
    border: 1px solid #f48e5f57;
    padding: 3em 2em 0.5em 2em;
    background: #ffffff87;
    color: $font-medium;
    border-radius: 1px;
    position: relative;
    .atom {
      @include font-size(16px);
      display: inline-block;
    }
    &__title {
      @include font-size(16px);
      color: $font-medium;
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
    &__button {
      color: palette(orange);
      position: absolute;
      right: 1em;
      top: 1em;
      cursor: pointer;
      &:after {
        content: "\2715";
        font-weight: bold;
        color: palette(orange);
        font-size: 14px;
      }
    }
  }
  &__button {
    text-align: right;
    color: palette(orange);
    font-weight: 600;
    cursor: pointer;
    .svg-icon {
      margin-right: 0.3em;
    }
  }
}
</style>
