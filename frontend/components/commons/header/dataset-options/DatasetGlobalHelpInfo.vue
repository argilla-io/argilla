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
    modal-title="Similarity search"
    :modal-custom="true"
    :modal-visible="visible"
    @close-modal="closeModal"
  >
    <div class="help-info__content">
      <p>
        Since <code>1.2.0</code> Argilla supports adding vectors to Argilla
        records which can then be used for finding the most similar records to a
        given one.
      </p>
      <p>
        This feature uses vector or semantic search combined with more
        traditional search (keyword and filter based). Vector search leverages
        machine learning to capture rich semantic features by embedding items
        (text, video, images, etc.) into a vector space, which can be then used
        to find "semantically" similar items.
      </p>
      <p>
        To benefit from this feature, your data team must include vectors
        associated with each record when they create the dataset.
      </p>
      <p>
        To learn more about this feature you can visit the
        <a
          href="https://docs.argilla.io/en/latest/guides/features/semantic-search.html"
          target="_blank"
          >documentation page</a
        >
      </p>
    </div>
    <div class="modal-buttons">
      <base-button
        class="primary link"
        href="https://docs.argilla.io/en/latest/guides/features/semantic-search.html"
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
    a {
      color: $primary-color;
      text-decoration: none;
      &:hover {
        color: darken($primary-color, 20%);
      }
    }
  }
  &__title {
    margin-bottom: 1em;
    @include font-size(14px);
    font-weight: 600;
    color: $black-87;
  }
}
code {
  background: $black-4;
}
</style>
