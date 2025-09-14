import { Platform, StyleSheet } from "react-native";
import { ThemedView } from "@/components/themed-view";
import { Card, Text, TextInput, Button } from "react-native-paper";
import { Avatar } from "react-native-paper";
import { useEffect, useState, useRef } from "react";
import { ScrollView } from "react-native";
import { Message } from "@/api/chatbotAPI";
import { getAnswerStream, getFilesHintStream } from "@/api/chatbotAPI";
import { ActivityIndicator, MD2Colors } from "react-native-paper";
import Markdown from "react-native-marked";
import { v4 as uuidv4 } from "uuid";

export default function Chatbot() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: uuidv4(),
      text: "Hello, I am your AI assistant, ask me anything about the files content, and I will try my best to help you.",
      type: "bot",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);

  const fetchHint = () => {
    const botId = uuidv4();

    // add placeholder bot message
    setMessages((prev) => [
      ...prev,
      {
        id: botId,
        text: "🤖 Getting the information...",
        type: "bot",
        timestamp: new Date(),
      },
    ]);

    getFilesHintStream(
      (text) => {
        // update bot message as stream comes in
        setMessages((prev) =>
          prev.map((m) => (m.id === botId ? { ...m, text } : m))
        );
      },
      () => console.log("stream complete")
    );
  };
  const fetchAnswer = () => {
    const botId = uuidv4();

    // add placeholder bot message
    setMessages((prev) => [
      ...prev,
      {
        id: botId,
        text: "🤖 Getting the answer...",
        type: "bot",
        timestamp: new Date(),
      },
    ]);
    getAnswerStream(
      input,
      (text) => {
        // update bot message as stream comes in
        setMessages((prev) =>
          prev.map((m) => (m.id === botId ? { ...m, text } : m))
        );
      },
      () => console.log("stream complete")
    ).then(() => {
      setIsLoading(false);
    });
  };
  useEffect((): void => {
    fetchHint();
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollViewRef.current && messages.length > 0) {
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  const handleSend = (): void => {
    if (input.trim() === "") {
      return;
    }
    setIsLoading(true);
    const updatedMessages: Message[] = [
      ...messages,
      {
        id: uuidv4(),
        text: input,
        type: "user",
        timestamp: new Date(),
      },
    ];
    setMessages(updatedMessages);
    fetchAnswer();
    setInput("");
  };

  return (
    <ThemedView style={styles.container}>
      <ScrollView
        ref={scrollViewRef}
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {messages.map((message) => (
          <ThemedView
            key={message.id}
            style={[
              styles.chatCard,
              message.type === "bot"
                ? styles.botMessageContainer
                : styles.userMessageContainer,
            ]}
          >
            {message.type === "bot" && <Avatar.Icon size={24} icon="robot" />}
            <Card style={styles.chatCard}>
              <Markdown
                value={message.text}
                flatListProps={{
                  initialNumToRender: 8,
                }}
              />
            </Card>
            {message.type === "user" && (
              <Avatar.Icon size={24} icon="account" />
            )}
          </ThemedView>
        ))}
        <ActivityIndicator animating={isLoading} color={MD2Colors.blue500} />
      </ScrollView>

      <Card style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          value={input}
          onChangeText={setInput}
          onSubmitEditing={handleSend}
          disabled={isLoading}
          label="Enter your question"
          right={<TextInput.Icon icon="send" />}
        />
      </Card>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  botMessageContainer: {
    flexDirection: "row",
    alignItems: "flex-start",
  },
  userMessageContainer: {
    flexDirection: "row",
    alignItems: "flex-end",
  },
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingTop: 20,
    paddingBottom: 20,
  },
  chatCard: {
    alignContent: "flex-start",
    marginBottom: 10,
    marginLeft: 10,
    marginRight: 10,
    marginTop: 1,
    width: "90%",
    height: "auto",
    alignSelf: "center",
    padding: 10,
    backgroundColor: "white",
  },
  chatCardContent: {
    padding: 16,
    fontSize: 17,
  },
  inputContainer: {
    position: "relative",
    marginBottom: 14,
    marginHorizontal: 16,
    padding: 14,
    backgroundColor: "transparent",
  },
  textInput: {
    backgroundColor: "transparent",
  },
});
