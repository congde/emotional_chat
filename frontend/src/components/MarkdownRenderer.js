import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import styled from 'styled-components';

const MarkdownContainer = styled.div`
  line-height: 1.7;
  word-wrap: break-word;
  overflow-wrap: break-word;

  h1, h2, h3, h4, h5, h6 {
    margin: 0.8em 0 0.4em 0;
    font-weight: 600;
    line-height: 1.4;
  }

  h1 { font-size: 1.4em; }
  h2 { font-size: 1.25em; }
  h3 { font-size: 1.15em; }
  h4 { font-size: 1.05em; }

  p {
    margin: 0.4em 0;
  }

  ul, ol {
    margin: 0.4em 0;
    padding-left: 1.5em;
  }

  li {
    margin: 0.2em 0;
  }

  code {
    background: rgba(0, 0, 0, 0.06);
    padding: 0.15em 0.4em;
    border-radius: 4px;
    font-size: 0.9em;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  }

  pre {
    background: rgba(0, 0, 0, 0.06);
    padding: 0.8em 1em;
    border-radius: 8px;
    overflow-x: auto;
    margin: 0.5em 0;

    code {
      background: none;
      padding: 0;
      font-size: 0.85em;
    }
  }

  blockquote {
    border-left: 3px solid #6366f1;
    margin: 0.5em 0;
    padding: 0.3em 0.8em;
    color: #555;
    background: rgba(99, 102, 241, 0.05);
    border-radius: 0 6px 6px 0;
  }

  table {
    border-collapse: collapse;
    margin: 0.5em 0;
    width: 100%;
    font-size: 0.9em;
  }

  th, td {
    border: 1px solid #ddd;
    padding: 0.4em 0.8em;
    text-align: left;
  }

  th {
    background: rgba(0, 0, 0, 0.04);
    font-weight: 600;
  }

  hr {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 0.8em 0;
  }

  strong {
    font-weight: 600;
  }

  a {
    color: #6366f1;
    text-decoration: none;
    &:hover {
      text-decoration: underline;
    }
  }

  img {
    max-width: 100%;
    border-radius: 8px;
  }

  & > *:first-child {
    margin-top: 0;
  }

  & > *:last-child {
    margin-bottom: 0;
  }
`;

const MarkdownRenderer = ({ content }) => {
  return (
    <MarkdownContainer>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {content}
      </ReactMarkdown>
    </MarkdownContainer>
  );
};

export default MarkdownRenderer;
