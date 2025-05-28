// import apiClient from './apiClient'; // We will now receive apiClient as an argument

const getTerms = async (apiClient, params) => {
  try {
    const response = await apiClient.get('/terms/', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching terms:', error);
    throw error;
  }
};

const getTermById = async (apiClient, termId) => {
  try {
    const response = await apiClient.get(`/terms/${termId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching term with ID ${termId}:`, error);
    throw error;
  }
};

const getTermStatistics = async (apiClient) => {
  try {
    const response = await apiClient.get('/terms/statistics');
    return response.data;
  } catch (error) {
    console.error('Error fetching term statistics:', error);
    throw error;
  }
};

const getDocumentsForTerm = async (apiClient, termId) => {
  try {
    const response = await apiClient.get(`/terms/${termId}/documents`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching documents for term ${termId}:`, error);
    throw error;
  }
};

// Добавьте другие функции для CRUD операций с терминами здесь при необходимости

export default {
  getTerms,
  getTermById,
  getTermStatistics,
  getDocumentsForTerm,
  // Экспортируйте другие функции здесь
}; 