<template>
  <div class="dataset-creation">
    <main class="container">
      <div class="dataset-creation__intro">
        <h1 class="dataset-creation__title">Welcome</h1>
        <h2 class="dataset-creation__subtitle">
          For more information on how to get started with Argilla please refer
          to the documentation.
        </h2>
      </div>
      <div class="dataset-creation__card card --hf">
        <h1 class="card__title">Start from an existing dataset</h1>
        <h2 class="card__subtitle">
          Easily load an existing dataset from the 🤗 Hugging Face Hub
        </h2>
        <p class="card__text">
          Paste a repository ID of the dataset you want to work with
        </p>
        <div class="dataset-creation__paste">
          <BaseInputContainer class="dataset-creation__input">
            <BaseInput
              class="search-area__input"
              v-model="repositoryId"
              placeholder="Repository ID"
            />
          </BaseInputContainer>
          <BaseButton class="primary" @click="loadDatasetFromHF"
            >Import Dataset</BaseButton
          >
        </div>
      </div>
      <div class="dataset-creation__card card">
        <h1 class="card__title">
          Fully configure the dataset from Argilla SDK
        </h1>
        <h2 class="card__subtitle">Recommended for custom datasets.</h2>
        <p class="card__text">
          Lorem ipsum dolor, sit amet consectetur adipisicing elit. Assumenda,
          ut sed excepturi repellendus sequi expedita, et tempora quibusdam
          laudantium debitis eos dolorum quidem id cupiditate iusto illum vel
          sunt reiciendis.
        </p>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  data: () => ({
    repositoryId: "openai/MMMLU",
  }),
  methods: {
    loadDatasetFromHF() {
      this.$emit("load-dataset-from-hf", this.repositoryId);
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-creation {
  height: 100%;
  background-color: var(--bg-accent-grey-1);
  min-height: 0;
  &__title {
    @include font-size(32px);
  }
  &__subtitle {
    @include font-size(18px);
    font-weight: 400;
    margin-bottom: 0;
  }
  &__card {
    padding: $base-space * 3;
    border-radius: $border-radius-m;
    border: 1px solid var(--bg-opacity-10);
    background: var(--bg-opacity-4);
    &.--hf {
      border-color: hsla(50, 100%, 50%, 0.8);
      background: hsla(50, 100%, 50%, 0.12);
    }
  }
  &__paste {
    display: flex;
    gap: $base-space * 2;
  }
  &__input {
    width: 300px;
    padding: 0 $base-space;
    border-radius: $border-radius;
    border: 1px solid var(--bg-opacity-10);
    background: var(--bg-accent-grey-1);
    &:focus-within {
      border-color: var(--fg-cuaternary);
    }
    input {
      @include input-placeholder {
        color: var(--fg-tertiary);
      }
    }
  }
}
.card {
  &__title {
    margin-top: 0;
    @include font-size(24px);
    font-weight: 500;
  }
  &__subtitle {
    margin-top: 0;
    @include font-size(16px);
    @include line-height(24px);
    font-weight: 400;
  }
  &__text {
    margin-top: 0;
    color: var(--fg-secondary);
    @include font-size(14px);
    @include line-height(24px);
    font-weight: 300;
  }
}
.container {
  display: flex;
  flex-direction: column;
  gap: $base-space * 4;
  height: 100%;
  max-width: 1500px;
  padding: $base-space * 4 $base-space * 8;
  margin: 0 auto;
  overflow: auto;
  @include media("<desktop") {
    padding: $base-space * 2;
  }
}
</style>
