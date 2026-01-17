#!/usr/bin/env node
import { SpeckitMcpServer } from "./server.js";

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args.includes("stdio")) {
    const server = new SpeckitMcpServer();
    await server.startStdio();
    console.error("Speckit MCP Server started via Stdio");
  } else if (args.includes("--port")) {
    const portIndex = args.indexOf("--port");
    const port = parseInt(args[portIndex + 1]);
    if (isNaN(port)) {
      console.error("Invalid port");
      process.exit(1);
    }
    const server = new SpeckitMcpServer();
    await server.startHttp(port);
  } else {
    console.error("Usage: node index.js [stdio] | [--port <number>]");
    process.exit(1);
  }
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
