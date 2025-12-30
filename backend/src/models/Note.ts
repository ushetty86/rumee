import mongoose, { Schema, Document } from 'mongoose';

export interface INote extends Document {
  userId: mongoose.Types.ObjectId;
  title: string;
  content: string;
  tags: string[];
  linkedEntities: mongoose.Types.ObjectId[];
  createdAt: Date;
  updatedAt: Date;
  embeddings?: number[];
}

const noteSchema = new Schema<INote>(
  {
    userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    title: { type: String, required: true },
    content: { type: String, required: true },
    tags: [{ type: String }],
    linkedEntities: [{ type: Schema.Types.ObjectId, ref: 'Entity' }],
    embeddings: [{ type: Number }],
  },
  { timestamps: true }
);

// Index for faster querying
noteSchema.index({ userId: 1, createdAt: -1 });
noteSchema.index({ tags: 1 });

export const Note = mongoose.model<INote>('Note', noteSchema);
