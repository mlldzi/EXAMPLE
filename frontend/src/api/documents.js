const getDocuments = async (apiClient, skip = 0, limit = 100, query = '') => {
  try {
    const params = { skip, limit };
    if (query) params.query = query;
    
    const response = await apiClient.get('/documents/', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching documents:', error);
    throw error;
  }
};

const getDocumentById = async (apiClient, docId) => {
  try {
    const response = await apiClient.get(`/documents/${docId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching document with ID ${docId}:`, error);
    throw error;
  }
};

const getTermsForDocument = async (apiClient, docId) => {
  try {
    const response = await apiClient.get(`/documents/${docId}/terms`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching terms for document ${docId}:`, error);
    throw error;
  }
};

const createDocument = async (apiClient, documentData) => {
  try {
    const response = await apiClient.post('/documents/', documentData);
    return response.data;
  } catch (error) {
    console.error('Error creating document:', error);
    throw error;
  }
};

// Добавьте другие функции для CRUD операций с документами здесь при необходимости

export default {
  getDocuments,
  getDocumentById,
  getTermsForDocument,
  createDocument,
  // Экспортируйте другие функции здесь
}; 