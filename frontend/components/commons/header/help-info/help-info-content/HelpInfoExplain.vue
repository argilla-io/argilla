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
    <p>
      Argilla enables you to register token attributions as part of the dataset
      records. For getting token attributions, you can use methods such as
      Integrated Gradients or SHAP. These methods try to provide a mechanism to
      interpret model predictions. More in
      <a
        class="primary link"
        href="https://docs.argilla.io/en/latest/tutorials/notebooks/monitoring-textclassification-shaptransformersinterpret-explainability.html"
        target="_blank"
        >docs
      </a>
    </p>
    <img src="images/help-info/explain.png" alt="token attributions" />
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
</template>

<style lang="scss" scoped>
.link {
  color: $primary-color;
  text-decoration: none;
  &:hover {
    color: darken($primary-color, 15%);
  }
}
img {
  display: flex;
  max-width: calc(100% - 16px);
  margin: 1.5em auto;
  border-radius: $border-radius;
  box-shadow: 0 2px 4px 3px $black-20;
}
</style>
