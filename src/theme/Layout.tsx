import React from 'react';
import Layout from '@theme-original/Layout';
import RAGChat from '@theme/RAGChat';

export default function LayoutWrapper(props) {
  return (
    <>
      <Layout {...props} />
      <RAGChat 
        websocketUrl={process.env.NODE_ENV === 'production' 
          ? 'wss://your-backend-domain.com/ws/chat' 
          : 'ws://localhost:8000/ws/chat'}
        enableTextSelection={true}
        showSources={true}
        maxMessages={50}
      />
    </>
  );
}