<template>
  <div class="config-card" :class="cardClass">
    <div class="config-card__header">
      <h3 class="config-card__title">{{ item.name }}</h3>
      <BaseButton v-if="removeIsAllowed" @click="remove"
        ><svgicon name="close" height="16" width="16"
      /></BaseButton>
    </div>
    <div class="config-card__content">
      <div class="config-card__row">
        <DatasetConfigurationSelector
          class="config-card__type"
          :options="typeOptions"
          v-model="item.type"
        />
        <BaseCheckbox v-model="item.required" class="config-card__required" />
      </div>
      <DatasetConfigurationInput v-model="item.title" placeholder="Title" />
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    item: {
      type: Object,
      required: true,
    },
    typeOptions: {
      type: Array,
      required: true,
    },
    removeIsAllowed: {
      type: Boolean,
      default: false,
    },
  },
  model: {
    prop: "type",
    event: "change",
  },
  data() {
    return {
      error: false,
    };
  },
  computed: {
    cardClass() {
      return {
        "--no-mapping": this.isNoMapping,
        "--error": this.error,
      };
    },
    noMapping() {
      return this.type === "no mapping";
    },
  },
  methods: {
    remove() {
      this.$emit("remove");
    },
  },
};
</script>

<style lang="scss" scoped>
.config-card {
  border-radius: $base-space;
  border: 1px solid hsla(216, 55%, 54%, 0.16);
  background: linear-gradient(
    180deg,
    hsla(216, 55%, 54%, 0.16) 0%,
    hsla(216, 55%, 54%, 0.1) 100%
  );
  &__header {
    display: flex;
    justify-content: space-between;
    padding: $base-space $base-space * 2;
    align-items: center;
    background: hsla(216, 55%, 54%, 0.04);
    border-bottom: 1px solid hsla(216, 55%, 54%, 0.06);
  }
  &__content {
    padding: $base-space $base-space * 2 $base-space * 2;
    display: flex;
    flex-direction: column;
    gap: $base-space;
  }
  &__title {
    margin: 0;
    font-weight: 500;
    @include font-size(14px);
  }
  &__row {
    display: flex;
    align-items: center;
    gap: $base-space;
    width: 100%;
  }
  &__type {
    flex: 1;
  }
  &__required {
    margin: 0;
    :deep(.checkbox__container) {
      border-color: var(--bg-opacity-20);
    }
  }
}
</style>
