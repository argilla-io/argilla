<template>
  <div
    class="record-metadata-info"
    ref="recordMetadataInfo"
    :style="{ marginTop: `${-topPosition}px` }"
  >
    <div class="table-info">
      <div
        v-for="{ titleKey, titleValue, data, classType } in tableInfo"
        :key="titleKey"
        :class="classType"
      >
        <div class="table-info__header">
          <div v-text="titleKey" />
          <div v-if="titleValue" v-text="titleValue" />
        </div>
        <div class="table-info__content">
          <div v-for="(value, key) in data" :key="key" class="table-info__row">
            <div class="table-info__key" v-text="key" />
            <div class="table-info__value" v-text="value" />
            <BaseActionTooltip
              class="table-info__copy"
              tooltip="Copied"
              tooltip-position="left"
            >
              <BaseButton
                class="table-info__copy__button"
                @click="$copyToClipboard(value)"
                ><svgicon name="copy" /></BaseButton
            ></BaseActionTooltip>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    record: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      topPosition: 0,
    };
  },
  computed: {
    tableInfo() {
      return [
        this.recordInfo,
        ...(this.record.metadata ? [this.metadataInfo] : []),
      ];
    },
    recordInfo() {
      return {
        titleKey: $nuxt.$t("recordInfo"),
        classType: "--intro",
        data: {
          ID: this.record.id,
          inserted_at: this.record.metadataInsertedAt,
          updated_at: this.record.metadataUpdatedAt,
        },
      };
    },
    metadataInfo() {
      return {
        titleKey: $nuxt.$t("metadata"),
        titleValue: $nuxt.$t("value"),
        classType: "--table",
        data: this.record.metadata,
      };
    },
  },
  mounted() {
    this.$nextTick(() => {
      const { bottom } = this.$refs.recordMetadataInfo.getBoundingClientRect();
      this.topPosition =
        bottom > window.innerHeight ? bottom - window.innerHeight + 24 : 0;
    });
  },
};
</script>

<style lang="scss" scoped>
.table-info {
  background: palette(white);
  min-width: 440px;
  border-radius: $border-radius-s;
  @include font-size(13px);
  overflow: hidden;
  &__content {
    max-height: 320px;
    overflow: auto;
  }
  &__header {
    display: flex;
    padding: $base-space $base-space * 2;
    background: $black-10;
    font-weight: 600;
    & > div:first-child {
      min-width: 100px;
    }
    .--table & {
      background: $black-6;
      border-top: 1px solid $black-10;
    }
  }
  &__row {
    position: relative;
    display: flex;
    padding: $base-space $base-space * 2;
    .--table & {
      border-top: 1px solid $black-10;
      &:nth-child(even) {
        background: $black-4;
      }
    }
    &:hover {
      .table-info__copy {
        display: block;
        z-index: 1;
      }
    }
  }
  &__key {
    min-width: 100px;
  }
  &__value {
    width: 100%;
    font-family: $quaternary-font-family;
    word-break: break-all;
    padding-right: $base-space * 3;
  }
  &__copy {
    position: absolute;
    right: $base-space;
    top: $base-space;
    display: none;
    flex-shrink: 0;
    &__button {
      padding: 0;
      color: $black-37;
    }
  }
}
</style>
