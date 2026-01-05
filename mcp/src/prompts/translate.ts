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
3. Ensure that any Markdown heading anchors remain functional after translation, such as:
  - [Original Anchor](#original-anchor) should become [Translated Anchor](#translated-anchor) after translation for headings.
  - Anchors specific rules:
    - Spaces and emojis are replaced with -
    - Other special characters are removed
4. Write the translation to a new file with the name "{original_filename}-${language}.{original_extension}" if you can do.

${text}`,
        },
      },
    ],
  };
};
