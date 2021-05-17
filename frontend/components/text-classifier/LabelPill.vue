<template>
  <div>
      <svgicon
        :class="['icon__predicted', predicted]"
        v-if="predicted"
        width="20"
        height="20"
        :name="predicted ? 'predicted-ko' : 'predicted-ok'"
      ></svgicon>
      <p v-for="label in labels" :key="label.index"  :class="['pill', isAnnotated(label) ? 'active' : '']" :title="label.class">
        <span class="pill__text">{{ label.class }} </span>
        <span class="pill__confidence" v-if="showConfidence">
          <ReNumeric
            class="radio-data__confidence"
            :value="decorateConfidence(label.confidence)"
            type="%"
            :decimals="2"
          ></ReNumeric>
        </span>
      </p>
    </div>
</template>

<script>
import 'assets/icons/predicted-ok';
import 'assets/icons/predicted-ko';
export default {
  props: {
    labels: {
      type: Array,
      required: true,
    },
    predicted: {
      type: String,
    },
    showConfidence: {
      type: Boolean,
      default: false,
    },
    annotationLabels: {
      type: Array,
    }
  },
  methods: {
    decorateConfidence(confidence) {
      return confidence * 100;
    },
    isAnnotated(label) {
      return label.confidence > 0.5 ? true : false
    }
  }
};
</script>

<style lang="scss" scoped>
%pill {
  display: inline-flex;
  width: auto;
  background: transparent;
  color: $lighter-color;
  border-radius: 3px;
  padding: 0.2em 1em;
  @include font-size(14px);
  margin-top: 0;
  margin-bottom: 0;
  border: 1px solid transparent;
  margin-right: 0.5em;
}
.annotations {
  position: absolute;
  right: 0;
  top: 0;
  display: block;
  height: 100%;
  overflow: auto;
  text-align: right;
  padding: 1em;
  .pill {
    text-align: left;
    display: inline-block;
    background: palette(grey, bg);
    border: none;
    display: inline-block;
    border-radius: 10px;
    &__text {
      word-break: break-all;
      white-space: break-spaces;
    }
  }
}
.predictions {
  margin-top: 1em;
  display: flex;
  flex-wrap: wrap;
  margin-right: -0.8em;
  margin-left: -0.8em;
  .pill {
    height: 40px;
    line-height: 40px;
    display: flex;
    width: 240px;
    align-items: center;
    margin-left: 0.8em;
    margin-right: 0.8em;
    margin-bottom: 1.6em;
    font-weight: bold;
    border: 1px solid palette(grey, smooth);
    border-radius: 5px;
    &__confidence {
      margin-right: 0;
      margin-left: auto;
    }
  }
}
.pill {
  @extend %pill;
  border: 1px solid $line-medium-color;
  color: $font-medium-color;
  margin-bottom: 0.5em;
  line-height: 1.4em;
  &__container {
    display: flex;
    margin-bottom: 1em;
  }
  &__text {
    display: inline-block;
    max-width: 200px;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }
  &__confidence {
    font-weight: bold;
    margin-left: 1em;
  }
  &.active {
    border-color: $secondary-color;
  }
}
.icon {
  &__predicted {
    display: block;
    text-align: right;
    margin-right: 0;
    margin-left: auto;
    margin-bottom: 1em;
    &.ko {
      fill: $error;
    }
    &.ok {
      fill: $success;
    }
  }
}
</style>
