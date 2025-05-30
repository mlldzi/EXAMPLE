// import apiClient from './apiClient'; // We will now receive apiClient as an argument

// API клиент для работы с терминами
const termsApi = {
  // Получение списка терминов с возможностью поиска и пагинации
  getTerms: async (apiClient, skip = 0, limit = 20, query = '') => {
    try {
      const params = { skip, limit };
      if (query) params.query = query;
      
      const response = await apiClient.get('/terms/', { params });
      return response.data;
    } catch (error) {
      console.error('Error getting terms:', error);
      throw error;
    }
  },

  // Получение одного термина по ID
  getTermById: async (apiClient, termId) => {
    try {
      const response = await apiClient.get(`/terms/${termId}`);
      return response.data;
    } catch (error) {
      console.error(`Error getting term ${termId}:`, error);
      throw error;
    }
  },

  // Создание нового термина
  createTerm: async (apiClient, termData) => {
    try {
      const response = await apiClient.post('/terms/', termData);
      return response.data;
    } catch (error) {
      console.error('Error creating term:', error);
      throw error;
    }
  },

  // Обновление существующего термина
  updateTerm: async (apiClient, termId, termData) => {
    try {
      const response = await apiClient.put(`/terms/${termId}`, termData);
      return response.data;
    } catch (error) {
      console.error(`Error updating term ${termId}:`, error);
      throw error;
    }
  },

  // Удаление термина
  deleteTerm: async (apiClient, termId) => {
    try {
      const response = await apiClient.delete(`/terms/${termId}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting term ${termId}:`, error);
      throw error;
    }
  },

  // Получение статистики использования терминов
  getTermsStatistics: async (apiClient) => {
    try {
      const response = await apiClient.get('/terms/statistics');
      return response.data;
    } catch (error) {
      console.error('Error getting terms statistics:', error);
      throw error;
    }
  },

  // Получение списка документов, связанных с термином
  getDocumentsForTerm: async (apiClient, termId) => {
    try {
      const response = await apiClient.get(`/terms/${termId}/documents`);
      return response.data;
    } catch (error) {
      console.error(`Error getting documents for term ${termId}:`, error);
      throw error;
    }
  },

  // Проверка конфликта термина
  checkTermConflict: async (apiClient, termData) => {
    try {
      const response = await apiClient.post('/terms/check-conflict', termData);
      return response.data;
    } catch (error) {
      console.error('Error checking term conflict:', error);
      throw error;
    }
  },

  // Массовое сохранение терминов
  bulkSaveTerms: async (apiClient, termsData) => {
    try {
      const response = await apiClient.post('/terms/bulk-save', termsData);
      return response.data;
    } catch (error) {
      console.error('Error bulk saving terms:', error);
      throw error;
    }
  }
};

export default termsApi; 