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
  <div class="origins">
    <text-spans-static
      v-if="record.prediction"
      v-once
      key="prediction"
      :dataset="dataset"
      origin="prediction"
      :record="record"
      class="prediction"
      :entities="getEntitiesByOrigin('prediction')"
    />
    <text-spans
      key="annotation"
      :dataset="dataset"
      origin="annotation"
      :record="record"
      class="annotation"
      :entities="getEntitiesByOrigin('annotation')"
    />
  </div>
</template>

<script>
export default {
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
    getEntitiesByOrigin(origin) {
      return this.record[origin]
        ? this.record[origin].entities.map((obj) => ({
            ...obj,
            origin: origin,
          }))
        : [];
    },
  },
};
</script>

<style lang="scss" scoped>
.origins > div:nth-child(2) {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  ::v-deep {
    .span__text {
      opacity: 1;
      color: transparent;
      .highlight {
        color: palette(grey, dark);
      }
    }
  }
}

.prediction {
  pointer-events: none;
  ::v-deep {
    .highlight__content {
      pointer-events: all;
    }
  }
}
.annotation {
  pointer-events: none;
  ::v-deep {
    .highlight__content {
      pointer-events: all;
    }
  }
}
::v-deep .highlight__tooltip__container {
  pointer-events: all;
  cursor: default;
}
::v-deep .highlight__tooltip {
  cursor: default;
}
</style>
