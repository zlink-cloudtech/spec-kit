import { describe, it, expect } from 'vitest';
import { translatePromptHandler, TRANSLATE_PROMPT_NAME } from '../src/prompts/translate.js';

describe('Prompts', () => {
  describe(TRANSLATE_PROMPT_NAME, () => {
    it('should generate correct prompt messages', async () => {
      const args = {
        language: 'Spanish',
        text: 'Hello world'
      };

      const result = await translatePromptHandler(args);

      expect(result.messages).toHaveLength(1);
      expect(result.messages[0].role).toBe('user');
      // @ts-ignore - content type checking
      expect(result.messages[0].content.type).toBe('text');
      // @ts-ignore
      expect(result.messages[0].content.text).toContain('Spanish');
      // @ts-ignore
      expect(result.messages[0].content.text).toContain('Hello world');
    });
  });
});
