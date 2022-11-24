<template>
  <transition-group name="chips" class="chips">
    <div class="chips__items" v-for="chip in chips" :key="chip.id">
      <label
        class="chip"
        :for="chip.id"
        v-text="chip.text"
        :class="[colorClass(chip.color_id), chip.is_activate ? 'activate' : 'not-activate']"
        @click="onChipsSelect(chip)"
      />
      <input :id="chip.id" type="checkbox" v-model="chip.is_activate" />
    </div>
  </transition-group>
</template>

<script>
export default {
  component: "ChipsComponent",
  props: {
    chips: {
      type: Array,
      required: true,
    },
    isMultiSelection: {
      type: Boolean,
      default: () => false,
    },
  },
  data() {
    return {
      cloneChips: [],
    };
  },
  methods: {
    onChipsSelect({ id, dataset_id }) {
      this.$emit("on-chips-select", { id, dataset_id });
    },
    colorClass(color) {
      return `color_${color}`
    }
  },
};
</script>

<style lang="scss" scoped>
.chips {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: $base-space;
  &__items {
    display: inline-flex;
  }
}
.chip {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-inline: 1em;
  border: none;
  min-height: 40px;
  min-width: 100px;
  border-radius: $border-radius-m;
  cursor: pointer;
  user-select: none;
  @include font-size(13px);
  font-weight: 600;
}

input[type="checkbox"] {
  display: none;
}
.chips__items {
  transition: all 1s;
}
.chips-enter,
.chips-leave-to {
  opacity: 0;
}
.chips-leave-active {
  position: absolute;
}

// ner colors

$colors: 50;
$hue: 360;
@for $i from 1 through $colors {
  $rcolor: hsla(($colors * $i) + calc($hue * $i / $colors), 100%, 88%, 1);
  .color_#{$i - 1} {
    color: darken($rcolor, 60%);
    border: $rcolor 3px solid;
    transition: background 0.3s ease-in-out;
    &:hover {
      background: mix(white, $rcolor, 80%);
      transition: background 0.3s ease-in;
    }
    &.activate {
      background: $rcolor;
      border: darken($rcolor, 15%) 3px solid;
    }
  }
}
</style>
