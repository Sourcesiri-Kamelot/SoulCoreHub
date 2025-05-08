import React from 'react';

const DisclaimerModal = ({ onAccept }) => (
  <div className="modal-overlay">
    <div className="modal-content">
      <h2>Before you enter</h2>
      <p>By using this AI society, you agree to our privacy terms and community standards.</p>
      <button onClick={onAccept}>I Accept</button>
    </div>
  </div>
);

export default DisclaimerModal;