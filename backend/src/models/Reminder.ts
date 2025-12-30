import mongoose, { Schema, Document } from 'mongoose';

export interface IReminder extends Document {
  userId: mongoose.Types.ObjectId;
  title: string;
  description?: string;
  dueDate: Date;
  type: 'task' | 'followup' | 'meeting_prep' | 'custom';
  priority: 'low' | 'medium' | 'high';
  linkedEntity: mongoose.Types.ObjectId;
  linkedEntityType: 'Note' | 'Person' | 'Meeting';
  completed: boolean;
  createdAt: Date;
  updatedAt: Date;
}

const reminderSchema = new Schema<IReminder>(
  {
    userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    title: { type: String, required: true },
    description: { type: String },
    dueDate: { type: Date, required: true },
    type: { 
      type: String, 
      enum: ['task', 'followup', 'meeting_prep', 'custom'],
      default: 'task'
    },
    priority: {
      type: String,
      enum: ['low', 'medium', 'high'],
      default: 'medium'
    },
    linkedEntity: { type: Schema.Types.ObjectId },
    linkedEntityType: {
      type: String,
      enum: ['Note', 'Person', 'Meeting']
    },
    completed: { type: Boolean, default: false },
  },
  { timestamps: true }
);

reminderSchema.index({ userId: 1, dueDate: 1 });
reminderSchema.index({ completed: 1 });

export const Reminder = mongoose.model<IReminder>('Reminder', reminderSchema);
