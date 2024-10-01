<template>
  <div class="config-card" :class="cardClass">
    <div class="config-card__header">
      <h3 class="config-card__title">{{ item.name }}</h3>
      <BaseButton v-if="removeIsAllowed" @click="remove"
        ><svgicon name="close" height="16" width="16"
      /></BaseButton>
    </div>
    <div class="config-card__content" :class="item.type.replace(/ /g, '')">
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
$validate-color: hsl(216, 55%, 54%);
$error-color: hsl(3, 100%, 69%);
$no-mapping-color: hsl(0, 0%, 50%);
.config-card {
  $this: &;
  border-radius: $base-space;
  border: 1px solid hsla(from $validate-color h s l / 0.16);
  background: linear-gradient(
    180deg,
    hsla(from $validate-color h s l / 0.16) 0%,
    hsla(from $validate-color h s l / 0.1) 100%
  );
  transition: all 0.3s ease-in;
  &__header {
    display: flex;
    justify-content: space-between;
    padding: $base-space $base-space * 2;
    align-items: center;
    background: hsla(from $validate-color h s l / 0.04);
    border-bottom: 1px solid hsla(from $validate-color h s l / 0.06);
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
  &:hover {
    transition: all 0.2s ease-in;
    box-shadow: 0 0 3px 1px var(--bg-opacity-10);
  }
  &:focus-within,
  &:focus {
    transition: all 0.3s ease-in;
    background: linear-gradient(
      180deg,
      hsla(from $validate-color h s l / 0) 0%,
      hsla(from $validate-color h s l / 0) 100%
    );
  }
  &:has(.dropdown__content) {
    transition: all 0.3s ease-in;
    background: linear-gradient(
      180deg,
      hsla(from $validate-color h s l / 0) 0%,
      hsla(from $validate-color h s l / 0) 100%
    );
  }
  &:has(.nomapping) {
    background: linear-gradient(
      180deg,
      hsla(from $no-mapping-color h s l / 0.16) 0%,
      hsla(from $no-mapping-color h s l / 0.1) 100%
    );
    #{$this}__header {
      background: hsla(from $no-mapping-color h s l / 0.04);
      border-bottom: 1px solid hsla(from $no-mapping-color h s l / 0.06);
    }
  }
  &:has(.error) {
    background: linear-gradient(
      180deg,
      hsla(from $error-color h s l / 0.16) 0%,
      hsla(from $error-color h s l / 0.1) 100%
    );
    #{$this}__header {
      background: hsla(from $error-color h s l / 0.04);
      border-bottom: 1px solid hsla(from $error-color h s l / 0.06);
    }
  }
}
</style>
