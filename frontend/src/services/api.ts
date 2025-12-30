import apiClient from './apiClient';

export const noteService = {
  async getNotes() {
    const response = await apiClient.get('/notes');
    return response.data;
  },

  async createNote(data: { title: string; content: string; tags?: string[] }) {
    const response = await apiClient.post('/notes', data);
    return response.data;
  },

  async updateNote(id: string, data: any) {
    const response = await apiClient.put(`/notes/${id}`, data);
    return response.data;
  },

  async deleteNote(id: string) {
    const response = await apiClient.delete(`/notes/${id}`);
    return response.data;
  },
};

export const peopleService = {
  async getPeople() {
    const response = await apiClient.get('/people');
    return response.data;
  },

  async createPerson(data: { name: string; email?: string; phone?: string }) {
    const response = await apiClient.post('/people', data);
    return response.data;
  },

  async updatePerson(id: string, data: any) {
    const response = await apiClient.put(`/people/${id}`, data);
    return response.data;
  },

  async deletePerson(id: string) {
    const response = await apiClient.delete(`/people/${id}`);
    return response.data;
  },
};

export const meetingService = {
  async getMeetings() {
    const response = await apiClient.get('/meetings');
    return response.data;
  },

  async createMeeting(data: any) {
    const response = await apiClient.post('/meetings', data);
    return response.data;
  },

  async updateMeeting(id: string, data: any) {
    const response = await apiClient.put(`/meetings/${id}`, data);
    return response.data;
  },

  async deleteMeeting(id: string) {
    const response = await apiClient.delete(`/meetings/${id}`);
    return response.data;
  },
};

export const reminderService = {
  async getReminders() {
    const response = await apiClient.get('/reminders');
    return response.data;
  },

  async createReminder(data: any) {
    const response = await apiClient.post('/reminders', data);
    return response.data;
  },

  async updateReminder(id: string, data: any) {
    const response = await apiClient.put(`/reminders/${id}`, data);
    return response.data;
  },

  async deleteReminder(id: string) {
    const response = await apiClient.delete(`/reminders/${id}`);
    return response.data;
  },
};

export const summaryService = {
  async getDailySummary(date?: string) {
    const response = await apiClient.get('/summaries/daily', { params: { date } });
    return response.data;
  },

  async getWeeklySummary() {
    const response = await apiClient.get('/summaries/weekly');
    return response.data;
  },
};
