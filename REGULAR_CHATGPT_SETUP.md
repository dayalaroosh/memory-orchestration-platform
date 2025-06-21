# Memory Triggers for Regular ChatGPT Conversations

This guide shows you how to add memory functionality to **regular ChatGPT conversations** (not just Custom GPTs) using trigger commands.

## 🎯 **What You'll Get**

✅ Use memory commands in **any ChatGPT conversation**  
✅ Trigger with natural language: `/remember`, `/recall`, etc.  
✅ Automatic memory detection for important information  
✅ Works across all your ChatGPT chats  

## 🔧 **Setup Process**

### **Step 1: Enable ChatGPT Actions**

ChatGPT Actions allow you to connect external APIs to regular conversations.

1. **Go to ChatGPT Settings**
   - Open [ChatGPT](https://chat.openai.com)
   - Click your profile → Settings → Beta Features
   - Enable "Actions" (if available)

2. **Add Memory Actions**
   - In any conversation, type: `@actions`
   - Click "Add Action" or "Configure Actions"
   - Import our schema (see below)

### **Step 2: Import Memory Action Schema**

Use this URL to import the memory actions:

```
https://raw.githubusercontent.com/dayalaroosh/memory-orchestration-platform/main/chatgpt-actions-schema.yaml
```

**Or copy this schema manually:**

```yaml
openapi: 3.1.0
info:
  title: Memory Assistant Actions
  description: Memory functions for regular ChatGPT conversations
  version: 1.0.0
servers:
  - url: https://memory-orchestration-platform.onrender.com

paths:
  /gpt/trigger-memory:
    post:
      operationId: triggerMemoryAction
      summary: Process memory commands like /remember and /recall
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                command:
                  type: string
                  enum: ["remember", "recall", "save", "search"]
                content:
                  type: string
                user_context:
                  type: string
              required: ["command", "content"]
      responses:
        "200":
          description: Memory action completed
```

### **Step 3: Configure Authentication**

- **Type**: API Key
- **Auth Type**: Custom  
- **Header Name**: `Authorization`
- **API Key**: `memory-gpt-2025-key`

## 🗣️ **How to Use Memory Commands**

### **Basic Commands**

| Command | Purpose | Example |
|---------|---------|---------|
| `/remember` | Save information | `/remember I prefer dark mode` |
| `/recall` | Search memories | `/recall my preferences` |
| `/save` | Save with emphasis | `/save this as important: Python is my favorite language` |
| `/search` | Find specific info | `/search for project notes` |

### **Natural Language Patterns**

The system recognizes these natural phrases:

```
✅ "Remember that I work at TechCorp"
✅ "Save this: I prefer concise responses"  
✅ "What did I say about my preferences?"
✅ "Find my notes about the project"
✅ "Recall what I told you about Python"
```

### **Automatic Detection**

The system automatically detects and saves:

- **Preferences**: "I prefer...", "I like..."
- **Goals**: "My goal is...", "I want to..."
- **Personal Info**: "I work at...", "I'm from..."
- **Projects**: "I'm working on...", "My project..."
- **Decisions**: "I decided to...", "I chose..."
- **Important Notes**: "Important:", "Note:"

## 💬 **Example Conversations**

### **Example 1: Saving Preferences**

```
You: "Remember that I prefer dark mode interfaces and concise responses when coding."

ChatGPT: "I'll save that preference for you.

*Triggering memory action...*

✅ Saved: I prefer dark mode interfaces and concise responses when coding.

Got it! I'll keep that in mind for future conversations. Dark mode is easier on the eyes, especially during long coding sessions."
```

### **Example 2: Recalling Information**

```
You: "/recall my coding preferences"

ChatGPT: "*Searching memories...*

🔍 Found 2 memories about 'coding preferences':

📝 I prefer dark mode interfaces and concise responses when coding
📝 I love Python programming and work as a data scientist

Based on your preferences, you like dark mode, concise responses, and Python programming. How can I help with your coding today?"
```

### **Example 3: Automatic Detection**

```
You: "I'm working on a memory orchestration platform using FastAPI and Next.js for my startup."

ChatGPT: "That sounds like an exciting project! A memory orchestration platform could be really valuable for AI workflows.

🤖 *Auto-detected memory-worthy content*
✅ Automatically saved: Working on memory orchestration platform using FastAPI and Next.js

FastAPI is great for building APIs quickly, and Next.js provides excellent React-based frontend capabilities. Are you planning to use any specific memory/vector databases?"
```

## 🎛️ **Advanced Usage**

### **Project-Specific Memories**

```
/remember for project MyApp: Using PostgreSQL for user data
/recall MyApp database decisions
```

### **Categorized Saving**

```
/save as goal: Launch product by December
/save as decision: Use Stripe for payments  
/save as insight: Users prefer simple interfaces
```

### **Contextual Searches**

```
/search for anything about databases
/recall decisions from last month
/find my goals for this quarter
```

## 🔄 **How It Works**

1. **You type a memory command** in any ChatGPT conversation
2. **ChatGPT recognizes the trigger** and calls our memory API
3. **The memory system processes** your command (save/search)
4. **ChatGPT responds** with confirmation and relevant information
5. **Your memories persist** across all future conversations

## 🛠️ **Troubleshooting**

### **Commands Not Working?**

1. **Check Actions Setup**: Ensure ChatGPT Actions are enabled
2. **Verify Schema**: Make sure the OpenAPI schema is imported correctly
3. **Test Authentication**: Try `/remember test` to see if API responds
4. **Check Syntax**: Use exact commands like `/remember` or `/recall`

### **No Memory Responses?**

1. **Wait for Processing**: Memory operations can take 2-3 seconds
2. **Try Different Queries**: Use broader search terms
3. **Check Storage**: Verify memories are being saved with `/recall test`

### **Alternative Triggers**

If `/` commands don't work, try these natural phrases:

```
"Remember that..."
"Save this information..."
"What did I tell you about..."
"Find my notes on..."
```

## 🚀 **Benefits**

✅ **Persistent Memory**: Information saved across all ChatGPT sessions  
✅ **Natural Commands**: Use simple `/remember` and `/recall` triggers  
✅ **Automatic Detection**: Important info is saved automatically  
✅ **Cross-Chat Memory**: Access memories from any conversation  
✅ **Smart Search**: Find relevant information with semantic search  
✅ **Project Organization**: Organize memories by projects or topics  

## 📱 **Mobile & Voice Support**

The memory commands work on:
- ✅ ChatGPT Web Interface
- ✅ ChatGPT Mobile App  
- ✅ Voice Conversations (say "slash remember" or "remember that")
- ✅ API Integrations

## 🔐 **Privacy & Security**

- 🔒 **Your Data**: Memories are stored securely with user isolation
- 🔑 **Authentication**: Protected by API key authentication
- 🗑️ **Control**: You can delete or modify memories anytime
- 🚫 **No Sharing**: Your memories are private to your conversations

## 📈 **Next Steps**

1. **Set up the Actions** using the schema above
2. **Test with simple commands** like `/remember test`
3. **Start using naturally** in your conversations
4. **Explore advanced features** like project organization

---

**🎉 You now have persistent memory in regular ChatGPT conversations!**

Try it out by typing: `/remember I just set up memory functionality and it's working great!` 