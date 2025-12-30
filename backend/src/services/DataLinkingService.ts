import { Note } from '../models/Note';
import { Person } from '../models/Person';
import { Meeting } from '../models/Meeting';
import { Reminder } from '../models/Reminder';
import AIService from './AIService';
import logger from '../utils/logger';
import mongoose from 'mongoose';

export class DataLinkingService {
  /**
   * Link new note to related entities (people, previous notes, meetings)
   */
  async linkNoteToEntities(
    userId: string,
    noteId: string,
    noteContent: string
  ): Promise<void> {
    try {
      // Extract entities from the note
      const entities = await AIService.extractEntities(noteContent);
      
      // Find related people
      if (entities.people && entities.people.length > 0) {
        const relatedPeople = await Person.find({
          userId: new mongoose.Types.ObjectId(userId),
          name: { $in: entities.people },
        });

        // Link the note to these people
        for (const person of relatedPeople) {
          person.linkedNotes.push(new mongoose.Types.ObjectId(noteId));
          await person.save();
        }
      }

      // Find related notes based on semantic similarity
      const allNotes = await Note.find({
        userId: new mongoose.Types.ObjectId(userId),
        _id: { $ne: noteId },
      }).limit(50);

      if (allNotes.length > 0) {
        const connections = await AIService.findConnections(
          noteContent,
          allNotes.map(n => n.content)
        );

        const currentNote = await Note.findById(noteId);
        if (currentNote) {
          for (const connection of connections) {
            if (connection.score > 0.6) {
              const relatedNote = allNotes[connection.index];
              currentNote.linkedEntities.push(relatedNote._id);
            }
          }
          await currentNote.save();
        }
      }

      logger.info(`Linked note ${noteId} to related entities`);
    } catch (error) {
      logger.error('Error linking note to entities:', error);
    }
  }

  /**
   * Link person to relevant notes and meetings
   */
  async linkPersonToRelevantData(
    userId: string,
    personId: string,
    personName: string
  ): Promise<void> {
    try {
      const allNotes = await Note.find({
        userId: new mongoose.Types.ObjectId(userId),
      }).limit(100);

      const allMeetings = await Meeting.find({
        userId: new mongoose.Types.ObjectId(userId),
      }).limit(100);

      const person = await Person.findById(personId);
      if (!person) return;

      // Find notes mentioning this person
      for (const note of allNotes) {
        if (note.content.toLowerCase().includes(personName.toLowerCase())) {
          if (!person.linkedNotes.includes(note._id)) {
            person.linkedNotes.push(note._id);
          }
        }
      }

      // Find meetings with this person
      for (const meeting of allMeetings) {
        if (meeting.title.toLowerCase().includes(personName.toLowerCase())) {
          if (!person.meetings.includes(meeting._id)) {
            person.meetings.push(meeting._id);
          }
        }
      }

      await person.save();
      logger.info(`Linked person ${personId} to relevant data`);
    } catch (error) {
      logger.error('Error linking person to relevant data:', error);
    }
  }

  /**
   * Link meeting to relevant notes and create action items
   */
  async linkMeetingToData(
    userId: string,
    meetingId: string,
    meetingNotes: string
  ): Promise<void> {
    try {
      // Generate action items
      const actionItems = await AIService.generateActionItems(meetingNotes);

      const meeting = await Meeting.findById(meetingId);
      if (meeting) {
        meeting.actionItems = actionItems;
        await meeting.save();
      }

      // Find related notes
      const allNotes = await Note.find({
        userId: new mongoose.Types.ObjectId(userId),
      }).limit(50);

      if (allNotes.length > 0) {
        const connections = await AIService.findConnections(
          meetingNotes,
          allNotes.map(n => n.content)
        );

        if (meeting) {
          for (const connection of connections) {
            if (connection.score > 0.6) {
              const relatedNote = allNotes[connection.index];
              meeting.linkedNotes.push(relatedNote._id);
            }
          }
          await meeting.save();
        }
      }

      logger.info(`Linked meeting ${meetingId} to related data`);
    } catch (error) {
      logger.error('Error linking meeting to data:', error);
    }
  }

  /**
   * Create automatic reminders based on meeting action items
   */
  async createRemindersFromActionItems(
    userId: string,
    meetingId: string
  ): Promise<void> {
    try {
      const meeting = await Meeting.findById(meetingId);
      if (!meeting || meeting.actionItems.length === 0) return;

      const threeDaysFromNow = new Date();
      threeDaysFromNow.setDate(threeDaysFromNow.getDate() + 3);

      for (const actionItem of meeting.actionItems) {
        const reminder = new Reminder({
          userId: new mongoose.Types.ObjectId(userId),
          title: actionItem,
          dueDate: threeDaysFromNow,
          type: 'task',
          priority: 'high',
          linkedEntity: meetingId,
          linkedEntityType: 'Meeting',
        });

        await reminder.save();
      }

      logger.info(`Created reminders from meeting ${meetingId}`);
    } catch (error) {
      logger.error('Error creating reminders from action items:', error);
    }
  }
}

export default new DataLinkingService();
