import React, { useState, useEffect } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";

const App = () => {
  const [files, setFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [file, setFile] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;  
  const pollingInterval = 10000;
  
  // Get file list
  const fetchFiles = async (page = 1) => {
    try {
	  const response = await axios.get(
        `http://127.0.0.1:8000/files/?skip=${(page - 1) * itemsPerPage}&limit=${itemsPerPage}`
        //`http://backend:8000/files/?skip=${(page - 1) * itemsPerPage}&limit=${itemsPerPage}`
      );
      setFiles(response.data);
      setCurrentPage(page);
    } catch (error) {
      console.error("Error fetching files:", error);
    }
  };

  // Upload file
  const uploadFile = async () => {
    if (!file) {
      alert("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:8000/upload/", formData, {
      //const response = await axios.post("http://backend:8000/upload/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      console.log("Upload successful:", response.data);
      fetchFiles();
      setShowUploadModal(false);
      setErrorMessage("");
	} catch (error) {
      console.error("Upload failed:", error.response?.data || error.message);
      setErrorMessage(error.response?.data?.detail || "An unexpected error occurred.");
	  setShowUploadModal(false);
	}
  };

  // Delete file
  const deleteFiles = async () => {
    if (selectedFiles.length === 0) {
      alert("You don't choose any files.");
      return;
    }

    const filesToDelete = files.filter(
      (file) => selectedFiles.includes(file.id) && (file.status === "Completed" || file.status === "Failed")
    );

    if (filesToDelete.length === 0) {
      alert("You can only delete files with status 'Completed' or 'Failed'.");
      return;
    }

    if (!window.confirm("Are you sure you want to delete the selected files?")) {
      return;
    }

    try {
      for (const fileId of selectedFiles) {
        await axios.delete(`http://127.0.0.1:8000/delete/${fileId}`);
        //await axios.delete(`http://backend:8000/delete/${fileId}`);
      }
      fetchFiles();
      setSelectedFiles([]);
    } catch (error) {
      console.error("Error deleting files:", error);
    }
  };

  useEffect(() => {
    fetchFiles();
	// Polling
    const intervalId = setInterval(() => {
      fetchFiles();
    }, pollingInterval);

    return () => clearInterval(intervalId);
  }, []);

  const hasNextPage = currentPage * itemsPerPage > files.length;
  
  return (
    <div className="container mt-5">
      <h1>File Management System</h1>
      <div className="d-flex justify-content-between mb-3">
        <button className="btn btn-danger" onClick={deleteFiles}>
          Delete
        </button>
        <button
          className="btn btn-primary"
          onClick={() => setShowUploadModal(true)}
        >
          Upload a new file
        </button>
      </div>

	  {errorMessage && (
	    <div className="alert alert-danger mt-2" role="alert">
		  {errorMessage}
	    </div>
	  )}

      {showUploadModal && (
        <div className="modal" style={{ display: "block" }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Upload File</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => {
				    setShowUploadModal(false);
					setErrorMessage("");
				  }}
                ></button>
              </div>
              <div className="modal-body">
                <input
                  type="file"
                  onChange={(e) => setFile(e.target.files[0])}
                  className="form-control"
                />
              </div>
              <div className="modal-footer">
                <button
                  className="btn btn-secondary"
                  onClick={() => {
				    setShowUploadModal(false);
					setErrorMessage("");
				  }}
                >
                  Cancel
                </button>
                <button className="btn btn-success" onClick={uploadFile}>
                  Save & Process
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <table className="table table-bordered">
        <thead>
          <tr>
            <th>
              <input
                type="checkbox"
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedFiles(
						files
							.filter((file) => file.status === "Completed" || file.status === "Failed")
							.map((file) => file.id)
					);
                  } else {
                    setSelectedFiles([]);
                  }
                }}
              />
            </th>
            <th>ID</th>
            <th>File Name</th>
            <th>Uploaded at</th>
			<th>File Type</th>
            <th>Status</th>
            <th>Preview</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr key={file.id}>
              <td>
                <input
                  type="checkbox"
                  checked={selectedFiles.includes(file.id)}
                  disabled={!(file.status === "Completed" || file.status === "Failed")}
				  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedFiles((prev) => [...prev, file.id]);
                    } else {
                      setSelectedFiles((prev) =>
                        prev.filter((id) => id !== file.id)
                      );
                    }
                  }}
                />
              </td>
              <td>{file.id}</td>
              <td>{file.file_name.replace(/\.[^/.]+$/, "")}</td>
              <td>{new Date(file.uploaded_at).toLocaleString()}</td>
              <td>{file.file_type}</td>
			  <td
				  style={{
					color:
					  file.status === "Uploading"
						? "black"
						: file.status === "Parsing"
						? "blue"
						: file.status === "Failed"
						? "red"
						: "green",
				  }}
			  >
			  	{file.status}
			  </td>
              <td>
                {file.status === "Completed" ? (
                  <a
                    href={`http://127.0.0.1:8000/parsed_content/${file.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-info btn-sm"
                  >
                    Open PDF
                  </a>
                ) : (
                  <button className="btn btn-secondary btn-sm" disabled>
                    Not Available
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
	  <div className="pagination">
		<button
		  className="btn btn-secondary"
		  disabled={currentPage === 1}
		  onClick={() => fetchFiles(currentPage - 1)}
		>
		  Previous
		</button>
		<span>--| Page {currentPage} |--</span>
		<button
		  className="btn btn-secondary"
		  onClick={() => fetchFiles(currentPage + 1)}
		  disabled={hasNextPage}
		>
		  Next
		</button>
	  </div>
    </div>
  );
};

export default App;
