#!/usr/bin/env node
import degit from "degit";

const repo = "akoskm/mcp-server-stdio";
const emitter = degit(repo, { cache: false, force: true, verbose: true });

const targetDir = process.argv[2] || ".";

emitter.clone(targetDir)
  .then(() => {
    console.log("Template copied!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("Failed to copy template:", error);
    process.exit(1);
  });