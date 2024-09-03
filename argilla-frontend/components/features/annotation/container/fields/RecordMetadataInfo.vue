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
          <div class="table-info__key" v-text="titleKey" />
          <div v-if="titleValue" v-text="titleValue" />
        </div>
        <div class="table-info__content">
          <div v-for="(value, key) in data" :key="key" class="table-info__row">
            <p class="table-info__key" :title="key" v-text="key" />
            <p class="table-info__value">
              {{ value }}
              <BaseActionTooltip
                class="table-info__copy"
                :tooltip="$t('copied')"
                tooltip-position="left"
              >
                <BaseButton
                  class="table-info__copy__button"
                  @click="$copyToClipboard(value)"
                  ><svgicon name="copy" /></BaseButton
              ></BaseActionTooltip>
            </p>
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
      bottomGap: 24,
    };
  },
  computed: {
    tableInfo() {
      return [this.recordInfo, this.metadataInfo];
    },
    recordInfo() {
      return {
        titleKey: $nuxt.$t("recordInfo"),
        classType: "--intro",
        data: {
          ID: this.record.id,
          inserted_at: this.record.insertedAt,
          updated_at: this.record.updatedAt,
        },
      };
    },
    metadataInfo() {
      if (!this.record.metadata) return [];

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
        bottom > window.innerHeight
          ? bottom - window.innerHeight + this.bottomGap
          : 0;
    });
  },
};
</script>

<style lang="scss" scoped>
.table-info {
  background: var(--bg-accent-grey-2);
  min-width: 440px;
  border-radius: $border-radius-s;
  overflow: hidden;
  @include font-size(13px);
  box-shadow: $shadow;
  &__content {
    max-height: 280px;
    overflow: auto;
  }
  &__header {
    display: flex;
    gap: $base-space;
    padding: $base-space $base-space * 2;
    font-weight: 600;
    & > div:first-child {
      min-width: 100px;
    }
    .--table & {
      background: var(--bg-opacity-6);
      border-top: 1px solid var(--bg-opacity-10);
      border-bottom: 1px solid var(--bg-opacity-10);
    }
  }
  &__row {
    position: relative;
    display: flex;
    gap: $base-space * 2;
    padding: $base-space $base-space * 2;
    .--table & {
      border-bottom: 1px solid var(--bg-opacity-10);
      &:nth-child(even) {
        background: var(--bg-opacity-4);
      }
    }
    &:hover {
      .table-info__copy {
        opacity: 1;
      }
    }
  }
  &__key {
    flex-basis: 44%;
    margin: 0;
    @include truncate;
    .--intro & {
      flex-basis: 100px;
    }
  }
  &__value {
    display: flex;
    gap: $base-space;
    flex-basis: 56%;
    align-items: center;
    justify-content: space-between;
    margin: 0;
    font-family: $quaternary-font-family;
    word-break: break-all;
    .--intro & {
      flex-basis: 100%;
    }
  }
  &__copy {
    opacity: 0;
    flex-shrink: 0;
    &__button {
      padding: 0;
      color: var(--fg-tertiary);
    }
  }
  :deep(.dropdown__content) {
    box-shadow: none;
  }
}
</style>
