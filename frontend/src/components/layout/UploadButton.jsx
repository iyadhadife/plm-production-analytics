import { useRef } from 'react';
import { Upload } from 'lucide-react';

export default function UploadButton({ onFileSelected }) {
  const inputRef = useRef(null);

  const handleChange = (event) => {
    const file = event.target.files[0];
    if (file) onFileSelected(file);
    event.target.value = null; // allow re-uploading the same file
  };

  return (
    <>
      <input type="file" ref={inputRef} onChange={handleChange} className="hidden-input" />
      <button onClick={() => inputRef.current.click()} className="primary-btn">
        <Upload size={18} />
        <span>Upload</span>
      </button>
    </>
  );
}
