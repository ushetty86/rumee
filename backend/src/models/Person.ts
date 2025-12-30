import mongoose, { Schema, Document } from 'mongoose';

export interface IPerson extends Document {
  userId: mongoose.Types.ObjectId;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  notes?: string;
  tags: string[];
  linkedNotes: mongoose.Types.ObjectId[];
  meetings: mongoose.Types.ObjectId[];
  reminders: mongoose.Types.ObjectId[];
  createdAt: Date;
  updatedAt: Date;
}

const personSchema = new Schema<IPerson>(
  {
    userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    name: { type: String, required: true },
    email: { type: String },
    phone: { type: String },
    company: { type: String },
    notes: { type: String },
    tags: [{ type: String }],
    linkedNotes: [{ type: Schema.Types.ObjectId, ref: 'Note' }],
    meetings: [{ type: Schema.Types.ObjectId, ref: 'Meeting' }],
    reminders: [{ type: Schema.Types.ObjectId, ref: 'Reminder' }],
  },
  { timestamps: true }
);

personSchema.index({ userId: 1, name: 1 });
personSchema.index({ email: 1 });

export const Person = mongoose.model<IPerson>('Person', personSchema);
