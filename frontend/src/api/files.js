import { getJson, getText } from './client.js';

export const fetchFiles = () => getJson('/api/files');

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return getJson('/api/upload', { method: 'POST', body: formData });
};

export const fetchExcelTable = (filename) =>
  getText(`/api/files/${encodeURIComponent(filename)}/table`);
