<template>
  <div class="text_field_component" :key="fieldText">
    <div class="title-area --body2">
      <span class="text_field_component__title-content">{{ title }}</span>
      <BaseActionTooltip
        class="text_field_component__tooltip"
        tooltip="Copied"
        tooltip-position="left"
      >
        <BaseButton
          title="Copy to clipboard"
          class="text_field_component__copy-button"
          @click.prevent="copyConversation"
        >
          <svgicon color="#acacac" name="copy" width="18" height="18" />
        </BaseButton>
      </BaseActionTooltip>
    </div>
    <div :id="`fields-content-${name}`" class="content-area --body1">
      <div class="flex-1 p-2 sm:p-6 justify-between flex flex-col">
        <div id="messages" class="flex flex-col space-y-4 p-3 overflow-y-auto">
          <div
            :id="`message-role-${message.role}`"
            class="chat-message"
            v-for="(message, index) in chatMessages"
            :key="index"
          >
            <div class="flex items-end">
              <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
                <div class="message-role-title">
                  <span class="px-4 py-2 rounded-lg inline-block rounded-tl-none bg-gray-300 text-gray-600">{{ message.role }}</span>
                </div>
                <div>
                  <span
                    class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600"
                    v-if="!message.editing"
                    @dblclick="editMessage(index)"
                  >{{ message.content }}</span>
                  <input
                    v-else
                    type="text"
                    v-model="message.content"
                    @blur="finishEditing(index)"
                    @keyup.enter="finishEditing(index)"
                    class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600"
                  />
                </div>
              </div>
              <div class="message-actions">
                <button @click="editMessage(index)">✏️</button>
                <button @click="deleteMessage(index)">🗑️</button>
                <button @click="regenerateMessage(index)">↪️</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <style scoped>
      ::highlight(search-text-highlight-{{name}}) {
        color: #ff675f;
      }
    </style>
  </div>
</template>

<script>
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
      chatMessages: [
        {
          role: "user",
          content: "Could you explain to me the difference between these two concepts? agricola and agricultura",
          editing: false,
        },
        {
          role: "system",
          content: "Sure! agricola is a noun and agricultura is a verb",
          editing: false,
        },
        {
          role: "user",
          content: "But what do they mean?",
          editing: false,
        },
        {
          role: "system",
          content: "agricola means farmer and agricultura means farming",
          editing: false,
        },
      ],
    };
  },
  methods: {
    async regenerateMessage(index) {
      const apiUrl = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct/v1/chat/completions";
      const apiKey = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"; // Replace with your Hugging Face API key

      for (let i = index + 1; i < this.chatMessages.length; i++) {
        const previousMessages = this.chatMessages.slice(0, i).map(msg => ({
          role: msg.role,
          content: msg.content,
        }));

        const response = await fetch(apiUrl, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${apiKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            model: "microsoft/Phi-3-mini-4k-instruct",
            messages: previousMessages,
            max_tokens: 500,
            stream: false,
          }),
        });

        const responseData = await response.json();
        const generatedContent = responseData.choices[0]?.message?.content || "Error generating response";

        this.$set(this.chatMessages, i, {
          ...this.chatMessages[i],
          content: generatedContent,
        });
      }
    },
    deleteMessage(index) {
      this.chatMessages.splice(index, 1);
    },
    editMessage(index) {
      this.chatMessages[index].editing = true;
    },
    finishEditing(index) {
      this.chatMessages[index].editing = false;
    },
    copyConversation() {
      const conversation = this.chatMessages.map(message => ({
        content: message.content,
        role: message.role,
      }));
      const conversationStr = JSON.stringify(conversation, null, 2);
      navigator.clipboard.writeText(conversationStr).then(() => {
        alert("Conversation copied to clipboard!");
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.text_field_component {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 2rem;
  background: lightgray;
  border-radius: 0.5rem;
  &:hover {
    .text_field_component__copy-button {
      opacity: 1;
    }
  }
  .title-area {
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #fff;
  }
  .content-area {
    white-space: pre-wrap;
    word-break: break-word;
  }
  div#message-role-user {
    background-color: lightgreen;
    right: 0;
    margin-left: auto;
  }
  .chat-message {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    padding: 10px;
    background-color: #d1e7dd;
    width: 30%;
    border-radius: 10px;
    .message-content {
      color: #333;
      padding: 10px;
      border-radius: 10px;
      margin-left: 10px;
      max-width: 80%;
      position: relative;
    }
    .message-role-title {
      display: flex;
      align-items: center;
      span {
        font-weight: bold;
      }
    }
    .message-actions {
      display: flex;
      gap: 5px;
      margin-left: auto;
      button {
        background-color: darkgray;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
        &:hover {
          background-color: #0056b3;
        }
      }
    }
  }
}
</style>