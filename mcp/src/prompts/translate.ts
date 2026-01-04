import { z } from "zod";

export const TRANSLATE_PROMPT_NAME = "translate-technical-document";

export const TranslatePromptSchema = z.object({
  language: z.enum(["CN", "EN"]).optional().describe("Target language (CN or EN)"),
  text: z.string().describe("The text to translate"),
});

export const translatePromptHandler = async ({ language = "CN", text }: z.infer<typeof TranslatePromptSchema>) => {
  return {
    messages: [
      {
        role: "user" as const,
        content: {
          type: "text" as const,
          text: `Please translate the following technical document to ${language}. Maintain technical accuracy and terminology.

1. Maintain the original layout and writing style of the technical document.
2. Do NOT translate technical terms, such as: MCP, API, LLM, etc.

${text}`,
        },
      },
    ],
  };
};
