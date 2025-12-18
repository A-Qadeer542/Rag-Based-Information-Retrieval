const API_BASE = "http://localhost:8000";

const pdfInput = document.getElementById("pdfInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");

const questionInput = document.getElementById("questionInput");
const askBtn = document.getElementById("askBtn");
const askStatus = document.getElementById("askStatus");
const answerBox = document.getElementById("answerBox");
const errorBox = document.getElementById("errorBox");

let hasUploaded = false;

const setStatus = (element, message) => {
  element.textContent = message;
};

const setLoading = (isLoading) => {
  uploadBtn.disabled = isLoading;
  askBtn.disabled = isLoading || !hasUploaded;
  pdfInput.disabled = isLoading;
};

const clearMessages = () => {
  setStatus(uploadStatus, "");
  setStatus(askStatus, "");
  answerBox.textContent = "";
  errorBox.textContent = "";
};

uploadBtn.addEventListener("click", async () => {
  clearMessages();
  if (!pdfInput.files || pdfInput.files.length === 0) {
    setStatus(uploadStatus, "Please choose a PDF first.");
    return;
  }

  const file = pdfInput.files[0];
  if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
    setStatus(uploadStatus, "Only PDF files are supported.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  setLoading(true);
  setStatus(uploadStatus, "Uploading and indexing...");

  try {
    const response = await fetch(`${API_BASE}/upload-pdf`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to upload PDF.");
    }

    const data = await response.json();
    hasUploaded = true;
    questionInput.disabled = false;
    askBtn.disabled = false;

    setStatus(
      uploadStatus,
      `PDF ready. Indexed ${data.chunks} chunks. You can ask questions now.`
    );
  } catch (error) {
    errorBox.textContent = error.message || "Upload failed.";
  } finally {
    setLoading(false);
  }
});

askBtn.addEventListener("click", async () => {
  clearMessages();
  if (!hasUploaded) {
    errorBox.textContent = "Please upload a PDF before asking questions.";
    return;
  }

  const question = questionInput.value.trim();
  if (!question) {
    errorBox.textContent = "Please enter a question.";
    return;
  }

  setLoading(true);
  setStatus(askStatus, "Retrieving answer...");

  try {
    const response = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to get answer.");
    }

    const data = await response.json();
    answerBox.textContent = data.answer;
  } catch (error) {
    errorBox.textContent = error.message || "Something went wrong.";
  } finally {
    setLoading(false);
  }
});


