<template>
  <span class="record__scroll__container">
    <span
      ref="list"
      :class="[
        'record__scroll--large',
        !allowScroll ? 'record__scroll--prevent' : '',
      ]"
    >
      <re-button :title="allowScroll ? 'prevent scroll' : 'allow scroll'" v-if="this.scrollHeight >= 800" class="record__scroll__button button-icon" @click="allowScroll = !allowScroll">
        <svgicon :name="allowScroll ? 'unlock' : 'lock'" width="15" height="14"></svgicon>
      </re-button>
      <span class="record__content" v-html="$highlightSearch(this.queryText, text)">
      </span>
    </span>
  </span>
</template>
<script>
import "assets/icons/lock";
import "assets/icons/unlock";

export default {
  props: {
    text: {
      type: String,
      required: true,
    },
    queryText: {
      type: String,
      default: undefined,
    },
  },
  data: () => ({
    allowScroll: false,
    scrollHeight: undefined,
  }),
  mounted() {
    if (this.$refs.list) {
      const padding = 2;
      this.scrollHeight = this.$refs.list.clientHeight + padding;
    }
  },
};
</script>
<style lang="scss">
.highlight-text {
  display: inline-block;
  // font-weight: 600;
  background: #ffbf00;
  line-height: 16px;
}
</style>
<style lang="scss" scoped>
.record {
  &__scroll {
    display: block;
    max-height: 300px;
    overflow: auto;
    border: 1px solid $line-smooth-color;
    @include font-size(14px);
    margin-bottom: 0.5em;
    &--large {
      display: block;
      overflow: auto;
      max-height: 800px;
      margin-bottom: 0.5em;
      ::v-deep .record__scroll__button {
        right: 0;
        top: 0;
        .svg-icon {
          margin-left: auto !important;
        }
      }
    }
    &__container {
      position: relative;
      display: block;
    }
    &__button {
      position: absolute;
      top: 10px;
      right: 10px;
      display: block;
      background: $lighter-color;
      border: 1px solid $primary-color;
      border-radius: 3px;
      height: 25px;
      width: 25px;
      padding: 0;
      display: flex;
      align-items: center;
      .svg-icon {
        margin: auto;
        fill: $primary-color;
      }
    }
    &--prevent {
      overflow: hidden;
    }
  }
}
</style>
