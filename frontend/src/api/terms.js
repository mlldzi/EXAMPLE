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

const getTermsByNames = async (apiClient, termNames) => {
  try {
    // Использование параметра query для поискового запроса
    // и фильтрация на клиенте для точного совпадения по имени
    const allTerms = await getTerms(apiClient, { query: termNames.join(' ') });
    return allTerms.filter(term => termNames.includes(term.name));
  } catch (error) {
    console.error('Error fetching terms by names:', error);
    throw error;
  }
};

const checkTermConflict = async (apiClient, termData) => {
  try {
    const response = await apiClient.post('/terms/check-conflict', termData);
    return response.data;
  } catch (error) {
    console.error('Error checking term conflict:', error);
    throw error;
  }
};

const bulkSaveTerms = async (apiClient, termsData) => {
  try {
    const response = await apiClient.post('/terms/bulk-save', termsData);
    return response.data;
  } catch (error) {
    console.error('Error during bulk save:', error);
    throw error;
  }
};

// Добавьте другие функции для CRUD операций с терминами здесь при необходимости

export default {
  getTerms,
  getTermById,
  getTermStatistics,
  getDocumentsForTerm,
  getTermsByNames,
  checkTermConflict,
  bulkSaveTerms
  // Экспортируйте другие функции здесь
}; 