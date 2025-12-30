import mongoose, { Schema, Document } from 'mongoose';

export interface IUser extends Document {
  email: string;
  password: string;
  name: string;
  preferences: {
    theme: 'light' | 'dark';
    notificationSettings: {
      reminderEmails: boolean;
      dailySummary: boolean;
      weeklyReport: boolean;
    };
  };
  createdAt: Date;
  updatedAt: Date;
}

const userSchema = new Schema<IUser>(
  {
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    name: { type: String, required: true },
    preferences: {
      theme: { type: String, enum: ['light', 'dark'], default: 'light' },
      notificationSettings: {
        reminderEmails: { type: Boolean, default: true },
        dailySummary: { type: Boolean, default: true },
        weeklyReport: { type: Boolean, default: false },
      },
    },
  },
  { timestamps: true }
);

userSchema.index({ email: 1 });

export const User = mongoose.model<IUser>('User', userSchema);
