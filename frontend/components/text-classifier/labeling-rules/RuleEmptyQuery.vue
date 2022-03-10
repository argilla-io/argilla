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
  <div class="rule-labels-definition">
    <div class="rule-labels-definition__info">
      <p class="rule__text">New query</p>
    </div>
    <div class="rule__labels" v-if="labels.length">
      <ClassifierAnnotationButton
        v-for="label in visibleLabels"
        :id="label.class"
        :key="`${label.class}`"
        :label="label"
        class="non-reactive label-button"
        :data-title="label.class"
        :value="label.class"
      >
      </ClassifierAnnotationButton>
    </div>
    <div v-else class="empty-labels">
      <p>This doesn't have any labels yet.</p>
      <p>
        To create new rules you need al least two labels. It's highly
        recommended to also annotate some records with these labels. Go to the
        annotation mode to
        <a href="#" @click.prevent="changeToAnnotationViewMode"
          >create the labels and annotate some records</a
        >.
      </p>
    </div>
    <div v-if="labels.length" class="empty-query">
      <p><strong>Introduce a query</strong> to define a rule.</p>
    </div>
  </div>
</template>
<script>
import { mapActions } from "vuex";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => {
    return {
      shownLabels: DatasetViewSettings.MAX_VISIBLE_LABELS,
    };
  },
  computed: {
    maxVisibleLabels() {
      return DatasetViewSettings.MAX_VISIBLE_LABELS;
    },
    labels() {
      return this.dataset.labels.map((l) => ({ class: l, selected: false }));
    },
    query() {
      return this.dataset.query.text;
    },
    sortedLabels() {
      return this.labels.slice().sort((a, b) => (a.score > b.score ? -1 : 1));
    },
    filteredLabels() {
      return this.sortedLabels.filter((label) =>
        label.class.toLowerCase().match(this.searchText)
      );
    },
    visibleLabels() {
      const availableNonSelected =
        this.shownLabels < this.filteredLabels.length
          ? this.shownLabels
          : this.shownLabels;
      let nonSelected = 0;
      return this.filteredLabels.filter((l) => {
        if (nonSelected < availableNonSelected) {
          nonSelected++;
          return l;
        }
      });
    },
  },
  methods: {
    ...mapActions({
      changeViewMode: "entities/datasets/changeViewMode",
    }),
    expandLabels() {
      this.shownLabels = this.filteredLabels.length;
    },
    collapseLabels() {
      this.shownLabels = this.maxVisibleLabels;
    },
    async changeToAnnotationViewMode() {
      await this.changeViewMode({
        dataset: this.dataset,
        value: "annotate",
      });
    },
  },
};
</script>
<style lang="scss" scoped>
%item {
  // width: calc(25% - 5px);
  min-width: 80px;
  max-width: 238px;
}
.rule-labels-definition {
  height: 100%;
  display: flex;
  flex-flow: column;
  &__info {
    display: flex;
  }
}
.feedback-interactions {
  .list__item--annotation-mode & {
    padding-right: 200px;
  }
  &__button {
    margin-top: auto;
    margin-bottom: 0 !important;
    align-self: flex-start;
  }
}
.label-button {
  @extend %item;
}
.empty-labels {
  a {
    outline: none;
    color: $primary-color;
    text-decoration: none;
  }
}
.empty-query {
  @include font-size(18px);
  color: palette(grey, medium);
  text-align: center;
  margin-bottom: 2em;
  margin-top: 0;
}
.label-button {
  margin: 5px;
}
.label-button ::v-deep .button {
  justify-content: center;
}
.label-button:not(.active) ::v-deep .button {
  background: #e0e1ff !important;
}
.rule {
  &__labels {
    margin-bottom: 1em;
    margin-left: -5px;
    margin-right: -5px;
  }
  &__text {
    width: 100%;
    color: palette(grey, medium);
    @include font-size(18px);
    font-weight: 600;
    margin-top: 0;
  }
}
</style>
