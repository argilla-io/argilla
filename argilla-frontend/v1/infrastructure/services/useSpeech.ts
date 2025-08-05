// eslint-disable-next-line import/no-named-as-default
import wordsToNumbers from "words-to-numbers";

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

type Commands = "OpenDatasets" | "SelectOption" | "Submit";

const sanitizeCommand: Record<
  Commands,
  {
    triggers: string[];
    handleParams?: (text: string) => null | unknown;
  }
> = {
  OpenDatasets: { triggers: ["open data sets"] },
  SelectOption: {
    triggers: ["select option", "select label", "select"],
    handleParams: (text) => {
      const params = text.split(" ").pop();

      const converted = wordsToNumbers(params);

      if (isNaN(Number(converted))) return null;

      return parseInt(converted as string);
    },
  },
  Submit: { triggers: ["submit", "submit this record", "submit record"] },
};

type Collector = (text: string) => void;

class Recognition {
  private readonly speaker: SpeechSynthesis;
  private readonly listener: any;
  private readonly collectors: ((text: string) => void)[] = [];

  private constructor() {
    this.speaker = window.speechSynthesis;
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    this.listener = new SpeechRecognition();
    this.listener.continuous = true;
    this.listener.interimResults = false;
    this.listener.lang = "en-US";
    this.listener.onresult = (event: any) => {
      const current = event.resultIndex;
      const result = event.results[current][0];
      const sanitized = result.transcript.trim().toLowerCase();

      if (this.lastTranscript !== sanitized) {
        // eslint-disable-next-line no-console
        console.log("Listening: ", sanitized);
        this.lastTranscript = sanitized;

        this.collectors.forEach((collect) => {
          collect(this.lastTranscript);
        });
      }

      setTimeout(() => {
        this.lastTranscript = "";
      }, 1000);
    };
  }

  speak(text: string) {
    const utterance = new SpeechSynthesisUtterance(text);
    this.speaker.speak(utterance);

    // eslint-disable-next-line no-console
    console.log("Speaking: ", text);
  }

  private lastTranscript = "";
  listen(collect: Collector) {
    this.collectors.push(collect);

    if (this.collectors.length === 1) {
      this.startListening();
    }
  }

  ignore(collect: Collector) {
    this.collectors.splice(this.collectors.indexOf(collect), 1);

    if (this.collectors.length === 0) {
      this.stopListening();
    }
  }

  private startListening() {
    this.listener.start();
  }

  private stopListening() {
    this.listener.stop();
  }

  // eslint-disable-next-line no-use-before-define
  private static recognitionInstance: Recognition;
  static create() {
    if (!this.recognitionInstance) {
      this.recognitionInstance = new Recognition();
    }

    return this.recognitionInstance;
  }
}

export const useSpeech = () => {
  const recognition = Recognition.create();

  const textToSpeech = (text: string) => {
    recognition.speak(text);
  };

  const speechCollect = (collect) => {
    recognition.listen(collect);
  };

  const explainCommands = () => {
    const currentCommands = Object.keys(sanitizeCommand).map(
      (key) => sanitizeCommand[key].triggers
    );

    recognition.speak(`This is our commands: ${currentCommands.join(", ")}`);
  };

  const waitCommands = (
    commands: Partial<Record<Commands, (params: any) => void>>
  ) => {
    const commandHandler = (text: string) => {
      if (text === "what can i do") {
        explainCommands();
      }

      const command = Object.keys(commands).find((key) =>
        sanitizeCommand[key].triggers.some((trigger) => text.includes(trigger))
      );

      if (sanitizeCommand[command]?.handleParams) {
        const params = sanitizeCommand[command]?.handleParams(text);

        if (command && params) {
          commands[command](params);
        }
        return;
      }

      if (command) {
        commands[command]();
      }
    };

    recognition.listen(commandHandler);

    return () => {
      recognition.ignore(commandHandler);
    };
  };

  return {
    textToSpeech,
    speechCollect,
    waitCommands,
    explainCommands,
  };
};
