#!/usr/bin/env node

/**
 * Memory Orchestration MCP Server
 * 
 * This MCP server provides memory orchestration capabilities for:
 * - Cursor IDE integration
 * - GitHub integration
 * - ChatGPT integration
 * - Cross-tool memory sharing
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import { readFileSync } from 'fs';
import { join } from 'path';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Configuration
const CONFIG = {
  MEMORY_API_URL: process.env.MEMORY_API_URL || 'http://localhost:8090',
  MEMORY_API_KEY: process.env.MEMORY_API_KEY || 'memory-gpt-2025-key',
  MCP_SERVER_NAME: 'memory-orchestration',
  MCP_SERVER_VERSION: '1.0.0'
};

// Debug logging
console.error('🔧 MCP Server Configuration:');
console.error(`   - API URL: ${CONFIG.MEMORY_API_URL}`);
console.error(`   - API Key: ${CONFIG.MEMORY_API_KEY ? '***' + CONFIG.MEMORY_API_KEY.slice(-4) : 'NOT SET'}`);
console.error(`   - Server: ${CONFIG.MCP_SERVER_NAME} v${CONFIG.MCP_SERVER_VERSION}`);

class MemoryOrchestrationServer {
  constructor() {
    this.server = new Server(
      {
        name: CONFIG.MCP_SERVER_NAME,
        version: CONFIG.MCP_SERVER_VERSION,
      },
      {
        capabilities: {
          resources: {},
          tools: {},
        },
      }
    );

    this.setupHandlers();
  }

  setupHandlers() {
    // List available resources
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      return {
        resources: [
          {
            uri: 'memory://recent',
            mimeType: 'application/json',
            name: 'Recent Memories',
            description: 'Recently stored memories across all tools'
          },
          {
            uri: 'memory://projects',
            mimeType: 'application/json', 
            name: 'Project Memories',
            description: 'Memories organized by project'
          },
          {
            uri: 'memory://actions',
            mimeType: 'application/json',
            name: 'Pending Actions',
            description: 'Action items and TODOs from various tools'
          }
        ]
      };
    });

    // Read specific resources
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;
      
      try {
        switch (uri) {
          case 'memory://recent':
            return await this.getRecentMemories();
          case 'memory://projects':
            return await this.getProjectMemories();
          case 'memory://actions':
            return await this.getPendingActions();
          default:
            throw new Error(`Unknown resource: ${uri}`);
        }
      } catch (error) {
        throw new Error(`Failed to read resource ${uri}: ${error.message}`);
      }
    });

    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'remember',
            description: 'Store a memory that can be accessed across all tools',
            inputSchema: {
              type: 'object',
              properties: {
                content: {
                  type: 'string',
                  description: 'The content to remember'
                },
                type: {
                  type: 'string',
                  enum: ['goal', 'action_item', 'decision', 'context', 'insight', 'reference', 'code_snippet', 'meeting_note'],
                  description: 'Type of memory'
                },
                project: {
                  type: 'string',
                  description: 'Project this memory belongs to'
                },
                source: {
                  type: 'string',
                  enum: ['cursor', 'chatgpt', 'github', 'slack', 'notion', 'manual'],
                  description: 'Source tool where this memory originated'
                },
                tags: {
                  type: 'array',
                  items: { type: 'string' },
                  description: 'Tags for categorization'
                }
              },
              required: ['content']
            }
          },
          {
            name: 'recall',
            description: 'Search and retrieve memories from across all tools',
            inputSchema: {
              type: 'object',
              properties: {
                query: {
                  type: 'string',
                  description: 'Search query to find relevant memories'
                },
                project: {
                  type: 'string',
                  description: 'Filter by specific project'
                },
                source: {
                  type: 'string',
                  enum: ['cursor', 'chatgpt', 'github', 'slack', 'notion', 'all'],
                  description: 'Filter by source tool'
                },
                limit: {
                  type: 'number',
                  description: 'Maximum number of results',
                  default: 10
                }
              },
              required: ['query']
            }
          },
          {
            name: 'get_context',
            description: 'Get relevant context for current work based on project/task',
            inputSchema: {
              type: 'object',
              properties: {
                current_task: {
                  type: 'string',
                  description: 'Description of current task or context'
                },
                project: {
                  type: 'string',
                  description: 'Current project name'
                },
                include_actions: {
                  type: 'boolean',
                  description: 'Include pending action items',
                  default: true
                }
              },
              required: ['current_task']
            }
          },
          {
            name: 'sync_from_tool',
            description: 'Sync memories from a specific tool (GitHub, Notion, etc.)',
            inputSchema: {
              type: 'object',
              properties: {
                tool: {
                  type: 'string',
                  enum: ['github', 'notion', 'slack'],
                  description: 'Tool to sync from'
                },
                project: {
                  type: 'string',
                  description: 'Project to sync'
                },
                since: {
                  type: 'string',
                  description: 'Sync changes since this date (ISO format)'
                }
              },
              required: ['tool']
            }
          }
        ]
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'remember':
            return await this.rememberTool(args);
          case 'recall':
            return await this.recallTool(args);
          case 'get_context':
            return await this.getContextTool(args);
          case 'sync_from_tool':
            return await this.syncFromToolTool(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`
            }
          ]
        };
      }
    });
  }

  // Memory API helpers
  async callMemoryAPI(endpoint, method = 'GET', data = null) {
    try {
      const config = {
        method,
        url: `${CONFIG.MEMORY_API_URL}${endpoint}`,
        headers: {
          'Authorization': `Bearer ${CONFIG.MEMORY_API_KEY}`,
          'Content-Type': 'application/json'
        }
      };

      if (data) {
        config.data = data;
      }

      const response = await axios(config);
      return response.data;
    } catch (error) {
      console.error(`Memory API error: ${error.message}`);
      throw new Error(`Memory API unavailable: ${error.message}`);
    }
  }

  // Resource handlers
  async getRecentMemories() {
    const memories = await this.callMemoryAPI('/gpt/search', 'POST', {
      query: '*',
      limit: 20
    });

    return {
      contents: [
        {
          uri: 'memory://recent',
          mimeType: 'application/json',
          text: JSON.stringify(memories, null, 2)
        }
      ]
    };
  }

  async getProjectMemories() {
    // Group memories by project
    const memories = await this.callMemoryAPI('/gpt/search', 'POST', {
      query: 'project:*',
      limit: 50
    });

    return {
      contents: [
        {
          uri: 'memory://projects',
          mimeType: 'application/json',
          text: JSON.stringify(memories, null, 2)
        }
      ]
    };
  }

  async getPendingActions() {
    const actions = await this.callMemoryAPI('/gpt/search', 'POST', {
      query: 'action_item todo task',
      limit: 30
    });

    return {
      contents: [
        {
          uri: 'memory://actions',
          mimeType: 'application/json',
          text: JSON.stringify(actions, null, 2)
        }
      ]
    };
  }

  // Tool implementations
  async rememberTool(args) {
    const { content, type = 'context', project, source = 'cursor', tags = [] } = args;

    const memoryData = {
      memory: content,
      metadata: {
        type,
        project,
        source,
        tags,
        timestamp: new Date().toISOString()
      }
    };

    const result = await this.callMemoryAPI('/gpt/memories', 'POST', memoryData);

    return {
      content: [
        {
          type: 'text',
          text: `✅ Memory stored successfully!\n\nContent: ${content}\nType: ${type}\nProject: ${project || 'N/A'}\nSource: ${source}\nID: ${result.memory_id || 'N/A'}`
        }
      ]
    };
  }

  async recallTool(args) {
    const { query, project, source, limit = 10 } = args;

    let searchQuery = query;
    if (project) searchQuery += ` project:${project}`;
    if (source && source !== 'all') searchQuery += ` source:${source}`;

    const results = await this.callMemoryAPI('/gpt/search', 'POST', {
      query: searchQuery,
      limit
    });

    const memories = results.results || [];
    const memoriesText = memories.length > 0 
      ? memories.map((mem, i) => `${i + 1}. ${mem.memory || mem.content} (${mem.source || 'unknown'})`).join('\n\n')
      : 'No memories found matching your query.';

    return {
      content: [
        {
          type: 'text',
          text: `🔍 Found ${memories.length} memories for "${query}":\n\n${memoriesText}`
        }
      ]
    };
  }

  async getContextTool(args) {
    const { current_task, project, include_actions = true } = args;

    // Search for relevant context
    const contextResults = await this.callMemoryAPI('/gpt/search', 'POST', {
      query: `${current_task} ${project || ''}`,
      limit: 10
    });

    let contextText = `📋 Context for: ${current_task}\n\n`;
    
    if (contextResults.results && contextResults.results.length > 0) {
      contextText += "Relevant memories:\n";
      contextResults.results.forEach((mem, i) => {
        contextText += `${i + 1}. ${mem.memory || mem.content}\n`;
      });
    } else {
      contextText += "No relevant context found.\n";
    }

    // Include pending actions if requested
    if (include_actions) {
      const actionResults = await this.callMemoryAPI('/gpt/search', 'POST', {
        query: 'action_item todo task',
        limit: 5
      });

      if (actionResults.results && actionResults.results.length > 0) {
        contextText += "\n📝 Pending actions:\n";
        actionResults.results.forEach((action, i) => {
          contextText += `${i + 1}. ${action.memory || action.content}\n`;
        });
      }
    }

    return {
      content: [
        {
          type: 'text',
          text: contextText
        }
      ]
    };
  }

  async syncFromToolTool(args) {
    const { tool, project, since } = args;

    // This would integrate with specific tool APIs
    // For now, return a placeholder
    return {
      content: [
        {
          type: 'text',
          text: `🔄 Sync from ${tool} requested.\n\nProject: ${project || 'All'}\nSince: ${since || 'All time'}\n\nThis feature is coming soon! We'll sync memories from ${tool} automatically.`
        }
      ]
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Memory Orchestration MCP Server running on stdio');
  }
}

// Start the server
const server = new MemoryOrchestrationServer();
server.run().catch(console.error); 