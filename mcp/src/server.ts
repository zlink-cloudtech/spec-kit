import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";
import { randomUUID } from "crypto";
import { TRANSLATE_PROMPT_NAME, TranslatePromptSchema, translatePromptHandler } from "./prompts/translate.js";

export class SpeckitMcpServer {
  private server: McpServer;

  constructor() {
    this.server = new McpServer({
      name: "speckit-mcp-server",
      version: "0.1.0",
    });

    this.registerPrompts();
  }

  private registerPrompts() {
    this.server.prompt(
      TRANSLATE_PROMPT_NAME,
      "Translate a technical document to a target language, suggest file naming convention: FILE_NAME-LANGUAGE.ext",
      TranslatePromptSchema.shape,
      translatePromptHandler
    );
  }

  async startStdio() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
  }

  async startHttp(port: number) {
    const app = express();
    app.use(express.json());

    app.use((req, res, next) => {
      console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
      next();
    });

    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: () => randomUUID(),
    });
    await this.server.connect(transport);

    app.get("/sse", async (req, res) => {
      await transport.handleRequest(req, res, req.body);
    });

    app.post("/messages", async (req, res) => {
      await transport.handleRequest(req, res, req.body);
    });

    // Handle root path for stateless HTTP requests
    app.post("/", async (req, res) => {
      await transport.handleRequest(req, res, req.body);
    });

    // Handle root path for SSE fallback
    app.get("/", async (req, res) => {
      await transport.handleRequest(req, res, req.body);
    });

    app.listen(port, () => {
      console.log(`Server is running on port ${port}`);
    });
  }
}
