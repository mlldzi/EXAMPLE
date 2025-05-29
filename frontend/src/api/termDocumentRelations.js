// import apiClient from './apiClient'; // We will now receive apiClient as an argument

const createTermDocumentRelation = async (apiClient, relationData) => {
  try {
    const response = await apiClient.post('/term_document_relations/', relationData);
    return response.data;
  } catch (error) {
    console.error('Error creating term-document relation:', error);
    throw error;
  }
};

const getRelationById = async (apiClient, relationId) => {
  try {
    const response = await apiClient.get(`/term_document_relations/${relationId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching relation with ID ${relationId}:`, error);
    throw error;
  }
};

const getRelations = async (apiClient, params) => {
  try {
    const response = await apiClient.get('/term_document_relations/', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching relations:', error);
    throw error;
  }
};

const updateRelation = async (apiClient, relationId, updateData) => {
  try {
    const response = await apiClient.put(`/term_document_relations/${relationId}`, updateData);
    return response.data;
  } catch (error) {
    console.error(`Error updating relation with ID ${relationId}:`, error);
    throw error;
  }
};

const deleteRelation = async (apiClient, relationId) => {
  try {
    const response = await apiClient.delete(`/term_document_relations/${relationId}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting relation with ID ${relationId}:`, error);
    throw error;
  }
};

const getTermConflictsReport = async (apiClient, termId) => {
  try {
    const response = await apiClient.get(`/term_document_relations/conflicts/${termId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching conflicts for term ${termId}:`, error);
    throw error;
  }
};

const getAllConflictsReport = async (apiClient) => {
  try {
    const response = await apiClient.get('/term_document_relations/conflicts');
    return response.data;
  } catch (error) {
    console.error('Error fetching all conflicts report:', error);
    throw error;
  }
};

// Добавьте другие функции для CRUD операций со связями здесь при необходимости

export default {
  createTermDocumentRelation,
  getRelationById,
  getRelations,
  updateRelation,
  deleteRelation,
  getTermConflictsReport,
  getAllConflictsReport,
  // Экспортируйте другие функции здесь
}; 