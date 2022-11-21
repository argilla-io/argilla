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
  <lazy-base-modal
    modal-class="modal-secondary"
    modal-position="modal-top-right"
    modal-title="Highlight colors in token attributions"
    :modal-custom="true"
    :modal-visible="visible"
    @close-modal="closeModal"
  >
    <div class="help-info__content">
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
    <div class="modal-buttons">
      <base-button
        class="primary link"
        href="https://docs.rubrix.ml/en/stable/tutorials/nlp_model_explainability.html"
        target="_blank"
        >More in docs</base-button
      >
      <base-button class="primary" @click="closeModal">Ok, got it!</base-button>
    </div>
  </lazy-base-modal>
</template>

<script>
import "assets/icons/support";
export default {
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    closeModal() {
      this.$emit("on-close");
    },
  },
};
</script>

<style lang="scss" scoped>
.help-info {
  &__content {
    margin-bottom: 2em;
    @include font-size(13px);
  }
  &__title {
    margin-bottom: 1em;
    @include font-size(14px);
    font-weight: 600;
    color: $black-87;
  }
}
</style>
