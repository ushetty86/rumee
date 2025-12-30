import axios from 'axios';
import logger from '../utils/logger';

interface OpenAIMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export class AIService {
  private apiKey: string;
  private baseURL = 'https://api.openai.com/v1';

  constructor() {
    this.apiKey = process.env.OPENAI_API_KEY || '';
  }

  /**
   * Generate embeddings for semantic similarity and linking
   */
  async generateEmbeddings(text: string): Promise<number[]> {
    try {
      const response = await axios.post(
        `${this.baseURL}/embeddings`,
        {
          input: text,
          model: 'text-embedding-3-small',
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      return response.data.data[0].embedding;
    } catch (error) {
      logger.error('Error generating embeddings:', error);
      throw error;
    }
  }

  /**
   * Extract entities (people, dates, topics) from text
   */
  async extractEntities(text: string): Promise<any> {
    try {
      const messages: OpenAIMessage[] = [
        {
          role: 'system',
          content: `You are an expert at extracting entities from text. Extract and return a JSON object with the following structure:
          {
            "people": ["name1", "name2"],
            "dates": ["date1", "date2"],
            "topics": ["topic1", "topic2"],
            "locations": ["location1"],
            "organizations": ["org1"]
          }`,
        },
        {
          role: 'user',
          content: `Extract entities from this text: "${text}"`,
        },
      ];

      const response = await axios.post(
        `${this.baseURL}/chat/completions`,
        {
          model: 'gpt-3.5-turbo',
          messages,
          temperature: 0.3,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      const content = response.data.choices[0].message.content;
      return JSON.parse(content);
    } catch (error) {
      logger.error('Error extracting entities:', error);
      throw error;
    }
  }

  /**
   * Generate daily summary from notes and meetings
   */
  async generateDailySummary(content: string): Promise<string> {
    try {
      const messages: OpenAIMessage[] = [
        {
          role: 'system',
          content: 'You are a professional assistant that creates concise, insightful daily summaries.',
        },
        {
          role: 'user',
          content: `Create a concise daily summary highlighting key points, action items, and follow-ups from this content:\n\n${content}`,
        },
      ];

      const response = await axios.post(
        `${this.baseURL}/chat/completions`,
        {
          model: 'gpt-3.5-turbo',
          messages,
          temperature: 0.5,
          max_tokens: 500,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      return response.data.choices[0].message.content;
    } catch (error) {
      logger.error('Error generating summary:', error);
      throw error;
    }
  }

  /**
   * Find connections between notes and entities
   */
  async findConnections(sourceText: string, targetTexts: string[]): Promise<any[]> {
    try {
      const messages: OpenAIMessage[] = [
        {
          role: 'system',
          content: `You are an expert at finding semantic connections between documents. 
          Return a JSON array with connection scores (0-1) and reasoning for each connection.`,
        },
        {
          role: 'user',
          content: `Find connections between this source text and the target texts.
          
          Source: "${sourceText}"
          
          Targets:
          ${targetTexts.map((t, i) => `${i + 1}. "${t}"`).join('\n')}
          
          Return format: [{"index": 0, "score": 0.8, "reason": "..."}]`,
        },
      ];

      const response = await axios.post(
        `${this.baseURL}/chat/completions`,
        {
          model: 'gpt-3.5-turbo',
          messages,
          temperature: 0.3,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      const content = response.data.choices[0].message.content;
      return JSON.parse(content);
    } catch (error) {
      logger.error('Error finding connections:', error);
      throw error;
    }
  }

  /**
   * Generate action items from meeting notes
   */
  async generateActionItems(meetingNotes: string): Promise<string[]> {
    try {
      const messages: OpenAIMessage[] = [
        {
          role: 'system',
          content: 'Extract actionable items from meeting notes. Return as JSON array of strings.',
        },
        {
          role: 'user',
          content: `Extract action items from these meeting notes:\n\n${meetingNotes}\n\nReturn format: ["action1", "action2"]`,
        },
      ];

      const response = await axios.post(
        `${this.baseURL}/chat/completions`,
        {
          model: 'gpt-3.5-turbo',
          messages,
          temperature: 0.3,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      const content = response.data.choices[0].message.content;
      return JSON.parse(content);
    } catch (error) {
      logger.error('Error generating action items:', error);
      throw error;
    }
  }
}

export default new AIService();
