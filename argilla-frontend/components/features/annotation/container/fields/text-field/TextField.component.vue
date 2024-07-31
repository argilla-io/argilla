<template>
  <div class="text_field_component" :key="fieldText">
    <div class="title-area --body2">
      <span class="text_field_component__title-content" v-text="title" />
      <BaseActionTooltip
        class="text_field_component__tooltip"
        tooltip="Copied"
        tooltip-position="left"
      >
        <BaseButton
          title="Copy to clipboard"
          class="text_field_component__copy-button"
          @click.prevent="$copyToClipboard(fieldText)"
        >
          <svgicon color="#acacac" name="copy" width="18" height="18" />
        </BaseButton>
      </BaseActionTooltip>
    </div>
    <div :id="`fields-content-${name}`" class="content-area --body1">
      <div :class="classes" v-if="!useMarkdown" v-html="fieldText" />
      <Sandbox v-else :fieldText="mock" :record="record" />
      <template>
        <style :key="name" scoped>
          ::highlight(search-text-highlight-{{name}}) {
            color: #ff675f;
          }
        </style>
      </template>
    </div>
  </div>
</template>

<script>
import { useTextFieldViewModel } from "./useTextFieldViewModel";

export default {
  name: "TextFieldComponent",
  props: {
    name: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    searchText: {
      type: String,
      default: "",
    },
    fieldText: {
      type: String,
      required: true,
    },
    useMarkdown: {
      type: Boolean,
      default: false,
    },
    record: {
      type: Object,
    },
  },
  data() {
    return {
      mock: `<link href="https://cdn.jsdelivr.net/npm/flowbite@2.4.1/dist/flowbite.min.css" rel="stylesheet" />
<style>
    body {
      background-color: #E20074
    }

    .bg-telekom-magenta {
        background-color: #E20074
    }
</style>

<div class="flex-1 p:2 sm:p-6 justify-between flex flex-col">
<div id="messages" class="flex flex-col space-y-4 p-3 overflow-y-auto scrollbar-thumb-blue scrollbar-thumb-rounded scrollbar-track-blue-lighter scrollbar-w-2 scrolling-touch">
<div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

<div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

</div>
</div>

<h2 class="ml-2">Vue JS</h2>

<script src="https://unpkg.com/vue@3/dist/vue.global.js"><\/script>

<div id="app">
  <p class="ml-2">{{ message }}</p>

  <input type="text" v-model="message" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="John" required />

  <br />

  <button class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800" @click="counter++">+</button>

  {{counter}}

  <button type="button" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800" @click="counter--">-</button>

  <h3>Data</h3>

  {{ JSON.stringify(fromOutside) }}
</div>

<script>
  const { createApp, ref } = Vue

  createApp({
    setup() {
      const message = ref('Hello vue!')
      const counter = ref(0)
      const fromOutside = ref("NONE")

      window.addEventListener('message', ({data})=>  {
        fromOutside.value = JSON.parse(data);
      });

      return {
        message,
        counter,
        fromOutside
      }
    }
  }).mount('#app')
<\/script>
`,
    };
  },
  computed: {
    classes() {
      return this.$language.isRTL(this.fieldText) ? "--rtl" : "--ltr";
    },
  },
  setup(props) {
    return useTextFieldViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.text_field_component {
  $this: &;
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: 2 * $base-space;
  background: palette(grey, 800);
  border-radius: $border-radius-m;
  &:hover {
    #{$this}__copy-button {
      opacity: 1;
    }
  }
  .title-area {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $base-space;
    color: $black-87;
  }
  .content-area {
    white-space: pre-wrap;
    word-break: break-word;
  }
  &__title-content {
    word-break: break-word;
    width: calc(100% - 30px);
  }
  &__tooltip {
    display: flex;
    align-self: flex-start;
  }
  &__copy-button {
    flex-shrink: 0;
    padding: 0;
    opacity: 0;
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
