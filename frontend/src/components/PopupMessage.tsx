import React from 'react';

function PopupMessage({ message, onClose }) {
  if (!message) {
    return null;
  }

  return (
    <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white p-5 border border-black z-50 shadow-lg">
      <p>{message}</p>
      <button onClick={onClose} className="mt-2 px-4 py-2 bg-blue-500 text-white rounded">Закрыть</button>
    </div>
  );
}

export default PopupMessage;
