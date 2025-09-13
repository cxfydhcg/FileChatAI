import { v4 as uuidv4 } from "uuid";

export interface Message {
  id: string;
  text: string;
  type: "user" | "bot";
  timestamp: Date;
}

const BASE_URL = "http://localhost:5000/api/";

export async function getAnswerStream(
  question: string,
  onChunk: (text: string) => void,
  onDone: () => void
) {
  const formData = new FormData();
  formData.append("question", question);

  try {
    const response = await fetch(`${BASE_URL}/chatbot/get_answer_stream`, {
      method: "POST",
      body: formData,
    });

    if (!response.body) throw new Error("ReadableStream not supported");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let partialText = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      partialText += decoder.decode(value, { stream: true });
      onChunk(partialText); // send current text back to UI
    }

    onDone();
  } catch (error) {
    console.error("Stream error:", error);
    onChunk("Sorry, there was an error.");
    onDone();
  }
}

export async function getFilesHintStream(
  onChunk: (text: string) => void,
  onDone: () => void
) {
  try {
    const response = await fetch(`${BASE_URL}/chatbot/get_files_hint_stream`, {
      method: "GET",
    });

    if (!response.body) throw new Error("ReadableStream not supported");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let partialText = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      partialText += decoder.decode(value, { stream: true });
      onChunk(partialText); // send current text back to UI
    }

    onDone();
  } catch (error) {
    console.error("Stream error:", error);
    onChunk("Sorry, there was an error.");
    onDone();
  }
}

// Export the Message interface for use in other components
