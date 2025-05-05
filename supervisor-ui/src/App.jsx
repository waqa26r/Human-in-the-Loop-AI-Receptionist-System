// src/App.jsx
import React, { useState, useEffect } from 'react';
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, query, where, onSnapshot, doc, updateDoc } from 'firebase/firestore';

// Firebase config
const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "your-sender-id",
  appId: "your-app-id"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

function App() {
  const [escalatedQuestions, setEscalatedQuestions] = useState([]);
  const [activeCalls, setActiveCalls] = useState([]);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [answerText, setAnswerText] = useState('');

  // Listen for escalated questions
  useEffect(() => {
    const q = query(collection(db, 'calls'), where('status', '==', 'escalated'));
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const calls = [];
      snapshot.forEach(doc => {
        const callData = doc.data();
        const pendingQuestions = callData.questions.filter(q => q.status === 'pending');
        calls.push({
          id: doc.id,
          ...callData,
          pendingQuestions
        });
      });
      setActiveCalls(calls);
      setEscalatedQuestions(calls.flatMap(call => call.pendingQuestions));
    });
    return () => unsubscribe();
  }, []);

  const handleAnswerSubmit = async () => {
    if (!selectedQuestion || !answerText.trim()) return;
    
    try {
      // Update the question with the answer
      const callRef = doc(db, 'calls', selectedQuestion.call_id);
      await updateDoc(callRef, {
        'questions': selectedQuestion.questions.map(q => 
          q.question_id === selectedQuestion.question_id ? 
          { ...q, status: 'answered', answer_text: answerText } : q
        )
      });

      // Submit to knowledge base
      await fetch('http://localhost:8000/submit_answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: selectedQuestion.question_id,
          answer_text: answerText,
          supervisor_id: 'user123' // In real app, use auth user ID
        })
      });

      setAnswerText('');
      setSelectedQuestion(null);
    } catch (error) {
      console.error('Error submitting answer:', error);
    }
  };

  return (
    <div className="supervisor-dashboard">
      <h1>AI Receptionist Supervisor Dashboard</h1>
      
      <div className="dashboard-container">
        <div className="active-calls">
          <h2>Active Calls ({activeCalls.length})</h2>
          <ul>
            {activeCalls.map(call => (
              <li key={call.id}>
                <strong>{call.customer_number}</strong>
                <ul>
                  {call.pendingQuestions.map(q => (
                    <li 
                      key={q.question_id} 
                      className={selectedQuestion?.question_id === q.question_id ? 'selected' : ''}
                      onClick={() => setSelectedQuestion({ ...q, call_id: call.id, questions: call.questions })}
                    >
                      {q.question_text}
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="answer-section">
          {selectedQuestion ? (
            <>
              <h3>Question from {selectedQuestion.customer_number}:</h3>
              <p>{selectedQuestion.question_text}</p>
              
              <textarea
                value={answerText}
                onChange={(e) => setAnswerText(e.target.value)}
                placeholder="Enter your answer..."
                rows={5}
              />
              
              <button onClick={handleAnswerSubmit}>Submit Answer</button>
            </>
          ) : (
            <p>Select a question to answer</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;