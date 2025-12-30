import { Note } from '../models/Note';
import { Meeting } from '../models/Meeting';
import AIService from './AIService';
import logger from '../utils/logger';
import mongoose from 'mongoose';
import { format } from 'date-fns';

export class SummaryService {
  /**
   * Generate daily summary of notes, meetings, and tasks
   */
  async generateDailySummary(userId: string, date?: Date): Promise<string> {
    try {
      const summaryDate = date || new Date();
      const dayStart = new Date(summaryDate);
      dayStart.setHours(0, 0, 0, 0);
      const dayEnd = new Date(summaryDate);
      dayEnd.setHours(23, 59, 59, 999);

      const userIdObj = new mongoose.Types.ObjectId(userId);

      // Get all notes, meetings, and reminders for the day
      const notes = await Note.find({
        userId: userIdObj,
        createdAt: { $gte: dayStart, $lte: dayEnd },
      });

      const meetings = await Meeting.find({
        userId: userIdObj,
        date: { $gte: dayStart, $lte: dayEnd },
      });

      // Compile content
      let compiledContent = '';

      if (notes.length > 0) {
        compiledContent += '## Notes from today\n';
        compiledContent += notes.map(n => `- ${n.title}: ${n.content}`).join('\n');
        compiledContent += '\n\n';
      }

      if (meetings.length > 0) {
        compiledContent += '## Meetings\n';
        compiledContent += meetings
          .map(
            m =>
              `- ${m.title} at ${format(m.date, 'HH:mm')}: ${m.notes || m.description}`
          )
          .join('\n');
        compiledContent += '\n\n';
      }

      if (!compiledContent) {
        return 'No activity recorded for today.';
      }

      // Generate summary
      const summary = await AIService.generateDailySummary(compiledContent);
      logger.info(`Generated daily summary for user ${userId}`);
      return summary;
    } catch (error) {
      logger.error('Error generating daily summary:', error);
      throw error;
    }
  }

  /**
   * Generate weekly summary
   */
  async generateWeeklySummary(userId: string): Promise<string> {
    try {
      const userIdObj = new mongoose.Types.ObjectId(userId);
      const weekStart = new Date();
      weekStart.setDate(weekStart.getDate() - 7);
      weekStart.setHours(0, 0, 0, 0);

      const notes = await Note.find({
        userId: userIdObj,
        createdAt: { $gte: weekStart },
      });

      const meetings = await Meeting.find({
        userId: userIdObj,
        date: { $gte: weekStart },
      });

      let compiledContent = '';
      compiledContent += `## Week of ${format(weekStart, 'MMM dd')}\n`;
      compiledContent += `\nNotes created: ${notes.length}\n`;
      compiledContent += `Meetings: ${meetings.length}\n\n`;

      if (notes.length > 0) {
        compiledContent += '### Key Topics\n';
        const tags = new Set(notes.flatMap(n => n.tags));
        compiledContent += Array.from(tags)
          .map(tag => `- ${tag}`)
          .join('\n');
      }

      const summary = await AIService.generateDailySummary(compiledContent);
      logger.info(`Generated weekly summary for user ${userId}`);
      return summary;
    } catch (error) {
      logger.error('Error generating weekly summary:', error);
      throw error;
    }
  }
}

export default new SummaryService();
