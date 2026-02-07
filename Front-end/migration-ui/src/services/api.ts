import axios from "axios";

const API = axios.create({
  baseURL: "https://orthodox-marie-jeanne-aswinxo-b6a366c1.koyeb.app",
});

export const uploadCSV = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await API.post("/classify", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};
