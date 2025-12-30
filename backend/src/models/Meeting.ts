import mongoose, { Schema, Document } from 'mongoose';

export interface IMeeting extends Document {
  userId: mongoose.Types.ObjectId;
  title: string;
  description?: string;
  attendees: mongoose.Types.ObjectId[];
  date: Date;
  duration: number;
  location?: string;
  notes?: string;
  actionItems: string[];
  linkedNotes: mongoose.Types.ObjectId[];
  createdAt: Date;
  updatedAt: Date;
}

const meetingSchema = new Schema<IMeeting>(
  {
    userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    title: { type: String, required: true },
    description: { type: String },
    attendees: [{ type: Schema.Types.ObjectId, ref: 'Person' }],
    date: { type: Date, required: true },
    duration: { type: Number }, // in minutes
    location: { type: String },
    notes: { type: String },
    actionItems: [{ type: String }],
    linkedNotes: [{ type: Schema.Types.ObjectId, ref: 'Note' }],
  },
  { timestamps: true }
);

meetingSchema.index({ userId: 1, date: -1 });
meetingSchema.index({ attendees: 1 });

export const Meeting = mongoose.model<IMeeting>('Meeting', meetingSchema);
