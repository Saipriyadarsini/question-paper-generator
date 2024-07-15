import React, { useState } from 'react';
import axios from 'axios';
import './App.css';  // Optional: import CSS for styling

function App() {
  const [file, setFile] = useState(null);
  const [downloadLink, setDownloadLink] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setErrorMessage(null);
    setDownloadLink(null);
    
    if (!file) {
      alert("Please upload a file first!");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/generate', formData, {
        responseType: 'blob',
      });

      if (response.status === 200) {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        setDownloadLink(url);
      } else {
        setErrorMessage('Error generating PDF');
      }
    } catch (error) {
      setErrorMessage('Error uploading file');
      console.error("There was an error uploading the file!", error);
    }
  };

  return (
    
    <div className="App">

      <h1>WELCOME TO QUESTION-CRAFT</h1>
      <br></br>
      <h2>Upload PDF to Generate Question Paper</h2>
      <br></br>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} accept=".pdf" />
        <button type="submit">Upload and Generate</button>
      </form>
      {errorMessage && (
        <div style={{color: 'red'}}>
          <p>{errorMessage}</p>
        </div>
        
      )}
      {downloadLink && (
        <div>
          <h2>Download Your Question Paper</h2>
          <a href={downloadLink} download="question_paper.pdf">Download PDF</a>
        </div>
      )}
    </div>
  );
}


export default App;
