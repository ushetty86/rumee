export interface INote {
  _id: string;
  userId: string;
  title: string;
  content: string;
  tags: string[];
  linkedEntities: string[];
  createdAt: string;
  updatedAt: string;
}

export interface IPerson {
  _id: string;
  userId: string;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  notes?: string;
  tags: string[];
  linkedNotes: string[];
  meetings: string[];
  reminders: string[];
  createdAt: string;
  updatedAt: string;
}

export interface IMeeting {
  _id: string;
  userId: string;
  title: string;
  description?: string;
  attendees: string[];
  date: string;
  duration: number;
  location?: string;
  notes?: string;
  actionItems: string[];
  linkedNotes: string[];
  createdAt: string;
  updatedAt: string;
}

export interface IReminder {
  _id: string;
  userId: string;
  title: string;
  description?: string;
  dueDate: string;
  type: 'task' | 'followup' | 'meeting_prep' | 'custom';
  priority: 'low' | 'medium' | 'high';
  linkedEntity: string;
  linkedEntityType: 'Note' | 'Person' | 'Meeting';
  completed: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface IUser {
  _id: string;
  email: string;
  name: string;
  preferences: {
    theme: 'light' | 'dark';
    notificationSettings: {
      reminderEmails: boolean;
      dailySummary: boolean;
      weeklyReport: boolean;
    };
  };
  createdAt: string;
  updatedAt: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    message: string;
    code: string;
  };
}
