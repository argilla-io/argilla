<template>
  <div>
    <span v-for="(text, index) in data" :key="index" class="record">
      <span :class="['record__item', isHtml(text) ? 'record--email' : '']">
        <span class="record__key">{{ index }}:</span>
        <RecordString :queryText="queryText" :text="text"></RecordString>
      </span>
    </span>
  </div>
</template>

<script>
export default {
  props: {
    data: {
      type: Object,
      required: true,
    },
    queryText: {
      type: String,
    },
  },
  methods: {
    isHtml(recordValue) {
      return recordValue.includes("<meta");
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  @include font-size(14px);
  white-space: pre-line;
  &__key {
    font-weight: lighter;
    margin-right: 0.5em;
    text-transform: uppercase;
    @include font-size(13px);
  }
  &__item {
    margin-right: 1em;
    display: inline-block;
  }
  &--email {
    display: block;
    ::v-deep table {
      width: calc(100% - 3em) !important;
      max-width: 700px !important;
      display: inline-block;
      overflow: scroll;
      td {
        min-width: 100px !important;
      }
      @include media(">xxl") {
        max-width: 1140px !important;
      }
    }
    ::v-deep img {
      display: none;
    }
    ::v-deep pre {
      white-space: pre-wrap !important;
    }
    ::v-deep .record__content {
      display: block;
      max-width: 748px !important;
      margin-left: 0 !important;
      word-break: break-word !important;
      @include media(">xxl") {
        max-width: 1140px !important;
      }
    }
    ::v-deep div.WordSection1 {
      word-break: break-all !important;
      p {
        font-family: initial !important;
      }
    }
  }
}
</style>
