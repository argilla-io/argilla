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
    <div class="origins">
      <text-spans
        v-for="origin in entitiesOrigin"
        :key="origin"
        :dataset="dataset"
        :origin="origin"
        :record="record"
        :class="origin"
        :entities="getEntitiesByOrigin(origin)"
      />
    </div>
    <div class="content__actions-buttons">
      <re-button
        v-if="record.status !== 'Validated'"
        class="button-primary"
        @click="onValidate(record)"
        >{{ record.status === "Edited" ? "Save" : "Validate" }}</re-button
      >
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex";

export default {
  data: function () {
    return {
      entitiesOrigin: ["prediction", "annotation"],
    };
  },
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    record: {
      type: Object,
      required: true,
    },
  },
  methods: {
    ...mapActions({
      validate: "entities/datasets/validateAnnotations",
    }),
    getEntitiesByOrigin(origin) {
      return origin === "annotation"
        ? this.record.annotatedEntities
        : (this.record.prediction && this.record.prediction.entities) || [];
    },
    async onValidate(record) {
      await this.validate({
        // TODO: Move this as part of token classification dataset logic
        dataset: this.dataset,
        agent: this.$auth.user.username,
        records: [
          {
            ...record,
            annotatedEntities: undefined,
            annotation: {
              entities: record.annotatedEntities,
              origin: "annotation",
            },
          },
        ],
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.content {
  position: relative;
  white-space: pre-wrap;
  & > div:nth-child(2) {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    ::v-deep {
      .span__text {
        opacity: 1;
      }
    }
  }
  &__input {
    padding-right: 200px;
  }
  &__actions-buttons {
    margin-right: 0;
    margin-left: auto;
    display: flex;
    min-width: 20%;
    .re-button {
      min-height: 32px;
      line-height: 32px;
      display: block;
      margin: 1.5em auto 0 0;
      & + .re-button {
        margin-left: 1em;
      }
    }
  }
}
.origins > div:nth-child(1) {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  ::v-deep {
    .span__text {
      opacity: 0;
    }
    .highlight__content__text {
      opacity: 0;
    }
  }
  ::v-deep .highlight-text {
    opacity: 0;
  }
}
// .prediction {
//   pointer-events: none;
//   ::v-deep {
//     .highlight__content {
//       pointer-events: all;
//     }
//   }
// }
// .annotation {
//   pointer-events: none;
//   * > {
//     pointer-events: all;
//   }
// }
</style>
